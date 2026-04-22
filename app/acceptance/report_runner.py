from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from app.acceptance.context_builder import build_acceptance_context
from app.acceptance.report_renderer import render_acceptance_markdown
from app.acceptance.report_validator import validate_acceptance_report
from app.core.env_loader import load_project_env, resolve_auth_loading_policy
from app.models.provider_factory import build_model_client


def build_acceptance_prompt(context: dict[str, str]) -> str:
    return (
        "You are performing final release acceptance for this repository.\n\n"
        "Review the following summarized inputs:\n"
        f"README_SUMMARY:\n{context['readme']}\n\n"
        f"ARCHITECTURE_SUMMARY:\n{context['architecture']}\n\n"
        f"TESTING_SUMMARY:\n{context['testing_conventions']}\n\n"
        f"CURRENT_SPRINT_SUMMARY:\n{context['current_sprint']}\n\n"
        f"RELEASE_NOTES_SUMMARY:\n{context['release_notes']}\n\n"
        f"GIT_STATUS_SUMMARY:\n{context['git_status']}\n\n"
        f"GIT_DIFF_STAT_SUMMARY:\n{context['git_diff_stat']}\n\n"
        "Return valid JSON only.\n\n"
        "Required keys:\n"
        "- system_summary\n"
        "- provider_risks\n"
        "- live_acceptance_configured\n"
        "- acceptance_status\n"
        "- evidence\n\n"
        "Rules:\n"
        "- treat GIT_STATUS_SUMMARY and GIT_DIFF_STAT_SUMMARY as authoritative repository-state inputs\n"
        "- the acceptance workspace may omit .git metadata intentionally; if git summaries are present, do not treat missing .git itself as a release risk\n"
        "- acceptance_status must be READY, NEEDS_REVIEW, or BLOCKED\n"
        "- provider_risks must be a list of concise strings\n"
        "- evidence must be a list of concise strings\n"
        "- keep system_summary concise and release-focused\n"
        "- do not wrap the JSON in markdown fences\n"
    )


def _extract_json_payload(model_output: str) -> dict:
    text = model_output.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def _parse_runtime_error_payload(exc: RuntimeError) -> dict | None:
    text = str(exc).strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _is_retryable_acceptance_error(exc: RuntimeError) -> bool:
    payload = _parse_runtime_error_payload(exc)
    if payload is not None:
        status = payload.get("status")
        if status in {502, 503, 504}:
            return True
        error_text = str(payload.get("error", "")).lower()
        if any(token in error_text for token in ("time-out", "timed out", "timeout", "temporarily unavailable")):
            return True
    message = str(exc).lower()
    return any(token in message for token in ("time-out", "timed out", "timeout", "temporarily unavailable"))


def _generate_with_retry(client, prompt: str) -> str:
    max_retries = int(os.getenv("CC_ACCEPTANCE_API_RETRIES", "1"))
    retry_delay_seconds = float(os.getenv("CC_ACCEPTANCE_API_RETRY_DELAY_SECONDS", "2"))
    attempt = 0
    last_error: RuntimeError | None = None
    while attempt <= max_retries:
        try:
            return client.generate(prompt)
        except RuntimeError as exc:
            last_error = exc
            if attempt >= max_retries or not _is_retryable_acceptance_error(exc):
                raise
            time.sleep(retry_delay_seconds)
            attempt += 1
    if last_error is not None:
        raise last_error
    raise RuntimeError("acceptance generation failed without a specific error")


def run_acceptance_report(repo_path: Path, model_provider: str, output_dir: Path, auth_source: str = "auto") -> dict:
    selected_provider, excluded_prefixes = resolve_auth_loading_policy(repo_path, model_provider, auth_source)
    load_project_env(repo_path, exclude_prefixes=excluded_prefixes)
    context = build_acceptance_context(repo_path)
    prompt = build_acceptance_prompt(context)
    client = build_model_client(selected_provider)
    raw_output = _generate_with_retry(client, prompt)
    report = _extract_json_payload(raw_output)
    validate_acceptance_report(report)

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "final_acceptance_report.json"
    markdown_path = output_dir / "final_acceptance_report.md"

    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(render_acceptance_markdown(report), encoding="utf-8")

    return {
        "provider": selected_provider,
        "report_json_path": str(json_path),
        "report_markdown_path": str(markdown_path),
        "acceptance_status": report["acceptance_status"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local model-backed acceptance report generation")
    parser.add_argument("--repo", required=True, help="Repository path to inspect")
    parser.add_argument("--provider", required=True, help="Model provider: glm5 or anthropic_api")
    parser.add_argument("--output-dir", default=".claude-code/acceptance", help="Acceptance artifact output directory")
    parser.add_argument("--auth-source", default="auto", choices=("auto", "cli", "env"))
    args = parser.parse_args(argv)

    repo_path = Path(args.repo).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_path / output_dir

    result = run_acceptance_report(repo_path, args.provider, output_dir, auth_source=args.auth_source)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

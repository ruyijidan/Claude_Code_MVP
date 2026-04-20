from __future__ import annotations

import argparse
import json
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


def run_acceptance_report(repo_path: Path, model_provider: str, output_dir: Path, auth_source: str = "auto") -> dict:
    selected_provider, excluded_prefixes = resolve_auth_loading_policy(repo_path, model_provider, auth_source)
    load_project_env(repo_path, exclude_prefixes=excluded_prefixes)
    context = build_acceptance_context(repo_path)
    prompt = build_acceptance_prompt(context)
    client = build_model_client(selected_provider)
    raw_output = client.generate(prompt)
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

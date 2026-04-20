from __future__ import annotations


def render_acceptance_markdown(report: dict) -> str:
    provider_risks = report.get("provider_risks", [])
    evidence = report.get("evidence", [])
    risk_lines = "\n".join(f"- {item}" for item in provider_risks) if provider_risks else "- None reported"
    evidence_lines = "\n".join(f"- {item}" for item in evidence) if evidence else "- No evidence recorded"
    live_configured = "Yes" if report.get("live_acceptance_configured") else "No"

    return (
        "# Final Acceptance Report\n\n"
        "## System Summary\n"
        f"{report.get('system_summary', '').strip()}\n\n"
        "## Provider Risks\n"
        f"{risk_lines}\n\n"
        "## Live Acceptance Configured\n"
        f"{live_configured}\n\n"
        "## Evidence\n"
        f"{evidence_lines}\n\n"
        f"ACCEPTANCE_STATUS: {report.get('acceptance_status', '').strip()}\n"
    )

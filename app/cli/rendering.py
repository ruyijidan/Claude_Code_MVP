from __future__ import annotations


def permission_summary(decision: dict) -> str:
    action = decision.get("action", decision.get("decision", "unknown"))
    risk = decision.get("risk", "unknown")
    boundary = decision.get("boundary", "unknown")
    reason = decision.get("reason", "")
    return f"action={action} risk={risk} boundary={boundary} reason={reason}"


def print_application_verification(result: dict) -> list[str]:
    application_verification = result.get("application_verification", {})
    if not application_verification.get("available"):
        return []
    lines = ["application verification:", str(application_verification.get("summary"))]
    findings = application_verification.get("findings", [])
    for finding in findings[:5]:
        lines.append(f"- {finding}")
    issues = application_verification.get("issues", [])
    if issues:
        lines.append("application issues:")
        for issue in issues[:5]:
            lines.append(f"- {issue}")
    return lines

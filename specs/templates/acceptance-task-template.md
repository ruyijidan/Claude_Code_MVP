You are running a final unattended release acceptance task inside an isolated repository copy.

Time budget:
- Work autonomously for up to {timeout_minutes} minutes.
- Do not ask follow-up questions.
- Do not wait for human confirmation.

Acceptance artifact requirements:
- Create `{report_markdown_path}`
- Create `{report_json_path}`

The markdown report must include:
1. A short system summary
2. Provider-facing release risks
3. Whether live provider acceptance appears configured in this workspace
4. A final line formatted exactly as `ACCEPTANCE_STATUS: READY`, `ACCEPTANCE_STATUS: NEEDS_REVIEW`, or `ACCEPTANCE_STATUS: BLOCKED`

The JSON report must be valid UTF-8 JSON and include these top-level keys:
- `system_summary`
- `provider_risks`
- `live_acceptance_configured`
- `acceptance_status`
- `evidence`

Task:
- Inspect this repository with emphasis on architecture, testing, and release acceptance expectations.
- Produce the required markdown and JSON artifacts.
- Keep the result concise, actionable, and suitable for release review.

from __future__ import annotations

import unittest

from app.acceptance.report_renderer import render_acceptance_markdown


class AcceptanceReportRendererTests(unittest.TestCase):
    def test_renders_markdown_with_required_sections(self) -> None:
        report = {
            "system_summary": "Summary",
            "provider_risks": ["Risk one"],
            "live_acceptance_configured": True,
            "acceptance_status": "READY",
            "evidence": ["Evidence one"],
        }

        markdown = render_acceptance_markdown(report)

        self.assertIn("# Final Acceptance Report", markdown)
        self.assertIn("## System Summary", markdown)
        self.assertIn("Risk one", markdown)
        self.assertIn("Yes", markdown)
        self.assertIn("ACCEPTANCE_STATUS: READY", markdown)

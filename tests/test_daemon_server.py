from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from socketserver import TCPServer

from app.daemon.server import create_handler
from app.daemon.service import DaemonService


class DaemonServerTests(unittest.TestCase):
    def test_http_endpoints_run_and_report_status(self) -> None:
        root = Path(__file__).resolve().parents[1]
        service = DaemonService(root / "specs")
        handler = create_handler(service)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with TCPServer(("127.0.0.1", 0), handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    repo_path = Path(tmp_dir)
                    base_url = f"http://127.0.0.1:{server.server_address[1]}"
                    request = urllib.request.Request(
                        f"{base_url}/tasks/run",
                        data=json.dumps(
                            {
                                "repo_path": str(repo_path),
                                "request_prompt": "Add a tool router and tests",
                                "task_name": "implement_feature",
                            }
                        ).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with opener.open(request) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                    self.assertEqual(payload["status"], "passed")

                    with opener.open(f"{base_url}/runs/status?repo_path={repo_path}") as response:
                        status_payload = json.loads(response.read().decode("utf-8"))
                    self.assertTrue(status_payload["available"])
                    self.assertEqual(status_payload["status"], "passed")

                    with opener.open(f"{base_url}/runs/latest?repo_path={repo_path}") as response:
                        latest_payload = json.loads(response.read().decode("utf-8"))
                    self.assertIn("agent_transitions", latest_payload)
            finally:
                server.shutdown()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()

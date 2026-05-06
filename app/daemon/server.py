from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from app.daemon.service import DaemonService


def create_handler(service: DaemonService):
    class DaemonHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if parsed.path == "/runs/latest":
                repo_path = _required_query_value(query, "repo_path")
                if repo_path is None:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "repo_path is required"})
                    return
                latest = service.latest_run(repo_path=repo_path)
                if latest is None:
                    self._write_json(HTTPStatus.NOT_FOUND, {"error": "no trajectory found"})
                    return
                self._write_json(HTTPStatus.OK, latest)
                return
            if parsed.path == "/runs/status":
                repo_path = _required_query_value(query, "repo_path")
                if repo_path is None:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "repo_path is required"})
                    return
                self._write_json(HTTPStatus.OK, service.run_status(repo_path=repo_path))
                return
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "unknown endpoint"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/tasks/run":
                self._write_json(HTTPStatus.NOT_FOUND, {"error": "unknown endpoint"})
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                content_length = 0
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            repo_path = payload.get("repo_path")
            request_prompt = payload.get("request_prompt")
            if not isinstance(repo_path, str) or not isinstance(request_prompt, str):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "repo_path and request_prompt are required"})
                return
            result = service.run_task(
                repo_path=repo_path,
                request_prompt=request_prompt,
                task_name=payload.get("task_name"),
                runtime_provider=payload.get("runtime_provider"),
            )
            self._write_json(HTTPStatus.OK, result)

        def log_message(self, format: str, *args) -> None:
            return

        def _write_json(self, status: HTTPStatus, payload: dict) -> None:
            body = service.to_json(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return DaemonHandler


def run_server(service: DaemonService, host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), create_handler(service))
    server.serve_forever()
    return server


def _required_query_value(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    if not values:
        return None
    return values[0]

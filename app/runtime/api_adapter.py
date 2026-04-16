from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from ipaddress import ip_address
from pathlib import Path

from app.runtime.local_runtime import LocalRuntimeAdapter


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


class AnthropicCompatibleAdapter(LocalRuntimeAdapter):
    provider_name = "anthropic_api"
    request_timeout_seconds = 60

    def __init__(self, *, provider_alias: str | None = None) -> None:
        super().__init__()
        self.provider_alias = provider_alias or self.provider_name

    def _config(self) -> dict[str, str]:
        return {
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "").strip(),
            "auth_token": os.getenv("ANTHROPIC_AUTH_TOKEN", "").strip(),
            "model": os.getenv("ANTHROPIC_MODEL", "").strip(),
            "max_tokens": os.getenv("ANTHROPIC_MAX_TOKENS", "1024").strip() or "1024",
            "bypass_proxy": os.getenv("ANTHROPIC_BYPASS_PROXY", "").strip().lower(),
        }

    def _should_bypass_proxy(self, base_url: str, bypass_proxy: str) -> bool:
        if bypass_proxy in {"1", "true", "yes", "on"}:
            return True
        parsed = urllib.parse.urlparse(base_url)
        hostname = parsed.hostname
        if not hostname:
            return False
        try:
            results = socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
        except socket.gaierror:
            return False
        for item in results:
            ip_text = item[4][0]
            try:
                resolved = ip_address(ip_text)
            except ValueError:
                continue
            if resolved.is_private or resolved.is_loopback or resolved.is_link_local:
                return True
        return False

    def _open_request(self, request: urllib.request.Request, *, bypass_proxy: bool):
        if not bypass_proxy:
            return urllib.request.urlopen(request, timeout=self.request_timeout_seconds)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        return opener.open(request, timeout=self.request_timeout_seconds)

    def provider_info(self) -> dict:
        info = super().provider_info()
        config = self._config()
        bypass_proxy = self._should_bypass_proxy(config["base_url"], config["bypass_proxy"])
        configured = all([config["base_url"], config["auth_token"], config["model"], config["max_tokens"]])
        info.update(
            {
                "provider": self.provider_alias,
                "binary": None,
                "binary_path": None,
                "available": configured,
                "delegates_prompt": configured,
                "base_url": config["base_url"],
                "model": config["model"],
                "transport": "anthropic_messages_api",
                "bypass_proxy": bypass_proxy,
            }
        )
        return info

    def can_delegate_prompt(self) -> bool:
        return self.provider_info()["available"]

    def _extract_text(self, payload: dict) -> str:
        content = payload.get("content", [])
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    if isinstance(text, str) and text:
                        parts.append(text)
            if parts:
                return "\n".join(parts).strip()
        if isinstance(payload.get("result"), str):
            return payload["result"]
        if isinstance(payload.get("output_text"), str):
            return payload["output_text"]
        return ""

    def execute_prompt(self, prompt: str, cwd: Path, *, auto_approve: bool = False) -> tuple[int, str, list[str]]:
        del cwd, auto_approve
        config = self._config()
        endpoint = _join_url(config["base_url"], "/v1/messages")
        bypass_proxy = self._should_bypass_proxy(config["base_url"], config["bypass_proxy"])
        request_payload = {
            "model": config["model"],
            "max_tokens": int(config["max_tokens"]),
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(request_payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": config["auth_token"],
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        command = ["POST", endpoint]
        try:
            with self._open_request(request, bypass_proxy=bypass_proxy) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            error_payload = {
                "provider": self.provider_alias,
                "endpoint": endpoint,
                "status": exc.code,
                "error": body,
            }
            return exc.code or 1, json.dumps(error_payload, ensure_ascii=False), command
        except urllib.error.URLError as exc:
            error_payload = {
                "provider": self.provider_alias,
                "endpoint": endpoint,
                "error": str(exc),
            }
            return 1, json.dumps(error_payload, ensure_ascii=False), command

        parsed = json.loads(body)
        result_payload = {
            "provider": self.provider_alias,
            "model": config["model"],
            "result": self._extract_text(parsed),
            "raw_response": parsed,
        }
        return 0, json.dumps(result_payload, ensure_ascii=False), command


class GLM5Adapter(AnthropicCompatibleAdapter):
    provider_name = "glm5"

    def __init__(self) -> None:
        super().__init__(provider_alias=self.provider_name)

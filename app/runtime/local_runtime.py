from __future__ import annotations

from app.runtime.ecc_adapter import ECCAdapter


class LocalRuntimeAdapter(ECCAdapter):
    provider_name = "local"

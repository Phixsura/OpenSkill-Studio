"""Correlation ID propagator — propagate correlation IDs through request chains."""
from __future__ import annotations
import secrets


class CorrelationPropagator:
    def __init__(self, header_name: str = "X-Correlation-ID"):
        self._header = header_name
        self._active: dict[str, list[str]] = {}

    def extract_or_create(self, headers: dict) -> dict:
        corr_id = headers.get(self._header, "")
        if not corr_id:
            corr_id = f"corr-{secrets.token_hex(12)}"
            created = True
        else:
            created = False
        return {"correlation_id": corr_id, "created": created, "header": self._header}

    def inject(self, corr_id: str, headers: dict) -> dict:
        headers[self._header] = corr_id
        return {"injected": True, "correlation_id": corr_id}

    def track_hop(self, corr_id: str, service: str) -> dict:
        self._active.setdefault(corr_id, []).append(service)
        return {"correlation_id": corr_id, "hops": len(self._active[corr_id])}

    def get_chain(self, corr_id: str) -> list[str]:
        return self._active.get(corr_id, [])

"""Request context propagator — propagate context across service boundaries."""
from __future__ import annotations
import secrets


class ContextPropagator:
    def __init__(self):
        self._active: dict[str, dict] = {}

    def create_context(self, user_id: str = "", tenant_id: str = "") -> dict:
        request_id = f"req-{secrets.token_hex(8)}"
        trace_id = f"trace-{secrets.token_hex(16)}"
        ctx = {"request_id": request_id, "trace_id": trace_id,
               "user_id": user_id, "tenant_id": tenant_id, "baggage": {}}
        self._active[request_id] = ctx
        return ctx

    def add_baggage(self, request_id: str, key: str, value: str) -> dict:
        if request_id in self._active:
            self._active[request_id]["baggage"][key] = value
            return {"added": True, "key": key}
        return {"added": False}

    def extract(self, request_id: str) -> dict | None:
        return self._active.get(request_id)

    def finish(self, request_id: str) -> dict:
        ctx = self._active.pop(request_id, None)
        return {"finished": ctx is not None, "request_id": request_id}

    def stats(self) -> dict:
        return {"active_contexts": len(self._active)}

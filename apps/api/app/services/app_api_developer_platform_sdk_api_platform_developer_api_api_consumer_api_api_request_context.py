"""API Consumer Request Context — attach contextual metadata to API requests."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class RequestContext:
    request_id: str
    trace_id: str = ""
    consumer_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    region: str = ""
    api_version: str = ""
    started_at: float = field(default_factory=time.time)
    metadata: dict[str, str] = field(default_factory=dict)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContext:
    def __init__(self) -> None:
        self._contexts: dict[tuple[str, str], RequestContext] = {}

    def create_context(self, installation_id: str, consumer_id: str, ip_address: str = "", user_agent: str = "", region: str = "", api_version: str = "") -> RequestContext:
        if not installation_id: raise ValueError("installation_id is required")
        request_id = f"req-{secrets.token_hex(12)}"
        trace_id = f"trace-{secrets.token_hex(16)}"
        ctx = RequestContext(request_id=request_id, trace_id=trace_id, consumer_id=consumer_id, ip_address=ip_address, user_agent=user_agent, region=region, api_version=api_version)
        self._contexts[(installation_id, request_id)] = ctx
        return ctx

    def get_context(self, installation_id: str, request_id: str) -> RequestContext | None:
        return self._contexts.get((installation_id, request_id))

    def add_metadata(self, installation_id: str, request_id: str, key: str, value: str) -> RequestContext:
        ctx = self._contexts.get((installation_id, request_id))
        if ctx is None: raise KeyError(f"Context {request_id} not found")
        ctx.metadata[key] = value
        return ctx

    def active_contexts(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._contexts if inst == installation_id)

    def contexts_by_region(self, installation_id: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for (inst, _), ctx in self._contexts.items():
            if inst == installation_id and ctx.region:
                result[ctx.region] = result.get(ctx.region, 0) + 1
        return result

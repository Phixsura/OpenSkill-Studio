"""Consumer API Request Context — propagate contextual metadata through request chains."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import secrets
import structlog

log = structlog.get_logger()

@dataclass
class RequestContext:
    context_id: str
    consumer_id: str
    trace_id: str = ""
    span_id: str = ""
    parent_span_id: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    baggage: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext:
    def __init__(self) -> None:
        self._contexts: dict[tuple[str, str], RequestContext] = {}

    def create(self, installation_id: str, consumer_id: str, attributes: dict[str, str] | None = None, baggage: dict[str, str] | None = None, parent_span_id: str | None = None, now: datetime | None = None) -> RequestContext:
        if not installation_id:
            raise ValueError("installation_id is required")
        trace_id = secrets.token_hex(16)
        span_id = secrets.token_hex(8)
        ctx = RequestContext(
            context_id=secrets.token_hex(8), consumer_id=consumer_id,
            trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id,
            attributes=attributes or {}, baggage=baggage or {},
            created_at=now or datetime.utcnow(),
        )
        self._contexts[(installation_id, ctx.context_id)] = ctx
        log.info("context_created", installation_id=installation_id, trace_id=trace_id)
        return ctx

    def get(self, installation_id: str, context_id: str) -> RequestContext | None:
        return self._contexts.get((installation_id, context_id))

    def add_attribute(self, installation_id: str, context_id: str, key: str, value: str) -> RequestContext:
        ctx = self._contexts.get((installation_id, context_id))
        if not ctx:
            raise ValueError("Context not found")
        if len(key) > 128 or len(value) > 1024:
            raise ValueError("Attribute key/value too long")
        ctx.attributes[key] = value
        return ctx

    def add_baggage(self, installation_id: str, context_id: str, key: str, value: str) -> RequestContext:
        ctx = self._contexts.get((installation_id, context_id))
        if not ctx:
            raise ValueError("Context not found")
        if len(ctx.baggage) >= 32:
            raise ValueError("Max 32 baggage items")
        ctx.baggage[key] = value
        return ctx

    def create_child_span(self, installation_id: str, context_id: str) -> RequestContext:
        parent = self._contexts.get((installation_id, context_id))
        if not parent:
            raise ValueError("Parent context not found")
        child = RequestContext(
            context_id=secrets.token_hex(8), consumer_id=parent.consumer_id,
            trace_id=parent.trace_id, span_id=secrets.token_hex(8), parent_span_id=parent.span_id,
            attributes=dict(parent.attributes), baggage=dict(parent.baggage),
            created_at=datetime.utcnow(),
        )
        self._contexts[(installation_id, child.context_id)] = child
        return child

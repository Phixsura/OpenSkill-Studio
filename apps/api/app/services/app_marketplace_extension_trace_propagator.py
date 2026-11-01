"""Trace Propagator — W3C Trace Context format for distributed tracing.

Implements:
- W3C traceparent header format: version-trace_id-parent_id-flags
- Context injection into outgoing requests
- Context extraction from incoming requests
- Baggage propagation (key-value pairs across services)
- Trace context creation for root spans
"""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets


@dataclass
class TraceContext:
    trace_id: str      # 32 hex chars (128 bit)
    parent_id: str     # 16 hex chars (64 bit)
    flags: int = 1     # 01 = sampled
    baggage: dict[str, str] = field(default_factory=dict)

    @property
    def sampled(self) -> bool:
        return bool(self.flags & 0x01)

    def to_traceparent(self) -> str:
        return f"00-{self.trace_id}-{self.parent_id}-{self.flags:02x}"

    def to_baggage(self) -> str:
        if not self.baggage:
            return ""
        return ",".join(f"{k}={v}" for k, v in self.baggage.items())


class TracePropagatorService:
    def new_context(self, sampled: bool = True,
                    baggage: dict[str, str] | None = None) -> TraceContext:
        """Create a new root trace context."""
        return TraceContext(
            trace_id=secrets.token_hex(16),
            parent_id=secrets.token_hex(8),
            flags=0x01 if sampled else 0x00,
            baggage=baggage or {})

    def child_context(self, parent: TraceContext) -> TraceContext:
        """Create a child span context (same trace, new span ID)."""
        return TraceContext(
            trace_id=parent.trace_id,
            parent_id=secrets.token_hex(8),
            flags=parent.flags,
            baggage=dict(parent.baggage))

    def inject(self, ctx: TraceContext) -> dict[str, str]:
        """Inject trace context into HTTP headers."""
        headers = {"traceparent": ctx.to_traceparent()}
        baggage = ctx.to_baggage()
        if baggage:
            headers["baggage"] = baggage
        return headers

    def extract(self, headers: dict[str, str]) -> TraceContext | None:
        """Extract trace context from HTTP headers."""
        traceparent = headers.get("traceparent", "")
        if not traceparent:
            return None

        parts = traceparent.split("-")
        if len(parts) != 4:
            return None

        version, trace_id, parent_id, flags_hex = parts
        if version != "00":
            return None
        if len(trace_id) != 32 or len(parent_id) != 16:
            return None

        try:
            flags = int(flags_hex, 16)
        except ValueError:
            return None

        baggage = {}
        baggage_header = headers.get("baggage", "")
        if baggage_header:
            for pair in baggage_header.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    baggage[k.strip()] = v.strip()

        return TraceContext(trace_id=trace_id, parent_id=parent_id,
                            flags=flags, baggage=baggage)

    def propagate(self, incoming_headers: dict[str, str],
                  baggage_additions: dict[str, str] | None = None) -> dict[str, str]:
        """Extract from incoming, create child, inject into outgoing."""
        parent = self.extract(incoming_headers)
        if not parent:
            parent = self.new_context()

        child = self.child_context(parent)
        if baggage_additions:
            child.baggage.update(baggage_additions)

        return self.inject(child)

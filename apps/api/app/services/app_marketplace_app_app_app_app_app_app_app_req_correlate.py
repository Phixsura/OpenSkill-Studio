"""Request correlation tracker — track requests across distributed services."""
from __future__ import annotations
import secrets
from collections import defaultdict


class RequestCorrelator:
    def __init__(self):
        self._requests: dict[str, list[dict]] = defaultdict(list)

    def start(self, correlation_id: str = "") -> dict:
        cid = correlation_id or f"req-{secrets.token_hex(8)}"
        return {"correlation_id": cid, "started": True}

    def add_hop(self, correlation_id: str, service: str, method: str,
                path: str, status: int, duration_ms: float) -> dict:
        hop = {"service": service, "method": method, "path": path,
               "status": status, "duration_ms": duration_ms,
               "hop_number": len(self._requests[correlation_id]) + 1}
        self._requests[correlation_id].append(hop)
        return hop

    def trace(self, correlation_id: str) -> dict:
        hops = self._requests.get(correlation_id, [])
        total_ms = sum(h["duration_ms"] for h in hops)
        services = list(set(h["service"] for h in hops))
        errors = [h for h in hops if h["status"] >= 400]
        return {"correlation_id": correlation_id, "hops": hops,
                "total_hops": len(hops), "total_ms": round(total_ms, 1),
                "services": services, "errors": len(errors),
                "success": len(errors) == 0}

    def stats(self) -> dict:
        return {"tracked_requests": len(self._requests),
                "total_hops": sum(len(h) for h in self._requests.values())}

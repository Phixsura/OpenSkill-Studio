"""Resource quota enforcer — enforce resource quotas per namespace."""
from __future__ import annotations

def enforce(namespace: str, resource: str, requested: float, limit: float, used: float) -> dict:
    available = limit - used
    allowed = requested <= available
    return {"namespace": namespace, "resource": resource, "allowed": allowed,
            "requested": requested, "available": round(available, 2),
            "used": used, "limit": limit}

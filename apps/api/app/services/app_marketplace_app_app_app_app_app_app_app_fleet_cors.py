"""Fleet CORS policy — audit CORS configurations."""
from __future__ import annotations
def fleet_cors_audit(services: list[dict]) -> dict:
    wildcard = [s for s in services if s.get("allow_origin") == "*"]
    no_cors = [s for s in services if not s.get("has_cors", True)]
    return {"total": len(services), "wildcard_origin": len(wildcard),
            "no_cors": len(no_cors), "secure": len(wildcard) == 0}

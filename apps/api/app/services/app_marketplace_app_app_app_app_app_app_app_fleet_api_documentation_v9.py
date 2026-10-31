"""Fleet API Documentation v9 — track API docs quality and coverage."""
from __future__ import annotations
def fleet_api_documentation_v9(apis: list[dict]) -> dict:
    documented = [a for a in apis if a.get("documented")]
    with_examples = [a for a in apis if a.get("has_examples")]
    openapi = [a for a in apis if a.get("openapi_spec")]
    return {"apis": len(apis), "documented": len(documented), "with_examples": len(with_examples),
            "openapi_spec": len(openapi), "healthy": len(documented) == len(apis)}

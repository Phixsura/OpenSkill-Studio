"""Fleet API OpenAPI v9 — track OpenAPI spec generation and linting."""
from __future__ import annotations
def fleet_api_openapi_v9(specs: list[dict]) -> dict:
    generated = [s for s in specs if s.get("generated")]
    linted = [s for s in specs if s.get("lint_passed")]
    errors = sum(s.get("lint_errors", 0) for s in specs)
    return {"specs": len(specs), "generated": len(generated), "linted": len(linted),
            "lint_errors": errors, "healthy": errors == 0}

"""Fleet API docs — track OpenAPI documentation coverage."""
from __future__ import annotations
def fleet_api_docs(endpoints: list[dict]) -> dict:
    documented = [e for e in endpoints if e.get("has_docs", False)]
    with_examples = [e for e in endpoints if e.get("has_examples", False)]
    pct = round(len(documented) / max(len(endpoints), 1) * 100, 1)
    return {"total": len(endpoints), "documented": len(documented), "with_examples": len(with_examples),
            "coverage_pct": pct, "complete": pct == 100}

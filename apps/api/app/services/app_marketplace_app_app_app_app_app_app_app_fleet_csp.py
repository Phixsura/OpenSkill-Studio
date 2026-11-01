"""Fleet CSP — track Content Security Policy adoption."""
from __future__ import annotations
def fleet_csp_status(services: list[dict]) -> dict:
    with_csp = [s for s in services if s.get("has_csp", False)]
    strict = [s for s in services if s.get("csp_strict", False)]
    return {"total": len(services), "with_csp": len(with_csp), "strict": len(strict),
            "coverage_pct": round(len(with_csp) / max(len(services), 1) * 100, 1)}

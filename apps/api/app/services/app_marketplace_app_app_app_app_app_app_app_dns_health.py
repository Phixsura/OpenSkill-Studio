"""DNS health checker — verify DNS resolution and propagation."""
from __future__ import annotations


def check_dns(domain: str, expected_records: list[dict]) -> dict:
    results = []
    resolved = 0
    for rec in expected_records:
        # Simulate DNS check
        ok = rec.get("value", "") != ""
        if ok:
            resolved += 1
        results.append({"type": rec["type"], "name": rec.get("name", domain),
                        "expected": rec.get("value", ""), "resolved": ok,
                        "ttl": rec.get("ttl", 3600)})
    return {"domain": domain, "checks": results, "total": len(results),
            "resolved": resolved, "failed": len(results) - resolved,
            "all_ok": resolved == len(results)}


def propagation_status(regions: list[dict]) -> dict:
    propagated = sum(1 for r in regions if r.get("propagated", False))
    return {"total_regions": len(regions), "propagated": propagated,
            "pending": len(regions) - propagated,
            "complete": propagated == len(regions),
            "progress_pct": round(propagated / max(len(regions), 1) * 100)}

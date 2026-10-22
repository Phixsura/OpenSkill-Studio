"""Performance budget — enforce load time and bundle size limits for app UI extensions."""


def create_budget(*, app_id: str, max_bundle_kb: int = 500, max_load_ms: int = 3000,
                    max_api_calls: int = 10) -> dict:
    return {"app_id": app_id, "max_bundle_kb": max_bundle_kb, "max_load_ms": max_load_ms,
            "max_api_calls": max_api_calls}


def check_budget(*, budget: dict, actual_bundle_kb: int, actual_load_ms: int,
                    actual_api_calls: int) -> dict:
    violations = []
    if actual_bundle_kb > budget["max_bundle_kb"]:
        violations.append({"metric": "bundle_size", "actual": actual_bundle_kb, "limit": budget["max_bundle_kb"], "unit": "KB"})
    if actual_load_ms > budget["max_load_ms"]:
        violations.append({"metric": "load_time", "actual": actual_load_ms, "limit": budget["max_load_ms"], "unit": "ms"})
    if actual_api_calls > budget["max_api_calls"]:
        violations.append({"metric": "api_calls", "actual": actual_api_calls, "limit": budget["max_api_calls"], "unit": "calls"})
    return {"within_budget": len(violations) == 0, "violations": violations,
            "score": round((1 - len(violations) / 3) * 100)}


def suggest_optimizations(*, violations: list[dict]) -> list[str]:
    suggestions = []
    for v in violations:
        if v["metric"] == "bundle_size":
            suggestions.append("Consider code splitting or lazy loading to reduce bundle size")
        elif v["metric"] == "load_time":
            suggestions.append("Optimize critical rendering path and defer non-essential resources")
        elif v["metric"] == "api_calls":
            suggestions.append("Batch API calls or implement client-side caching")
    return suggestions

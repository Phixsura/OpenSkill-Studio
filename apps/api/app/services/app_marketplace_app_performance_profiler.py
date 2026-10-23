"""Performance profiler — trace and analyze app performance bottlenecks."""


def create_profile(*, app_id: str, duration_ms: int, samples: list[dict]) -> dict:
    if not samples:
        return {"app_id": app_id, "hotspots": [], "total_ms": duration_ms, "bottleneck": None}
    hotspots = sorted(samples, key=lambda s: -s.get("duration_ms", 0))[:5]
    bottleneck = hotspots[0] if hotspots else None
    return {"app_id": app_id, "total_ms": duration_ms, "hotspots": hotspots,
            "bottleneck": bottleneck, "sample_count": len(samples)}


def analyze_slow_queries(*, queries: list[dict], threshold_ms: int = 100) -> dict:
    slow = [q for q in queries if q.get("duration_ms", 0) > threshold_ms]
    return {"total": len(queries), "slow_count": len(slow), "slow_queries": slow[:10],
            "avg_ms": round(sum(q.get("duration_ms", 0) for q in queries) / max(len(queries), 1))}


def suggest_optimizations(*, profile: dict) -> list[str]:
    suggestions = []
    if profile.get("total_ms", 0) > 1000:
        suggestions.append("Consider async processing for long-running operations")
    bottleneck = profile.get("bottleneck")
    if bottleneck and bottleneck.get("type") == "db":
        suggestions.append("Add database indexes for slow queries")
    if bottleneck and bottleneck.get("type") == "network":
        suggestions.append("Implement connection pooling and caching")
    return suggestions or ["Performance looks good!"]

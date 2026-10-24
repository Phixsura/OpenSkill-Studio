"""Network latency mapper — map network latency between services."""
from __future__ import annotations
from collections import defaultdict


def build_latency_map(measurements: list[dict]) -> dict:
    by_pair: dict[str, list[float]] = defaultdict(list)
    for m in measurements:
        key = f"{m['source']}→{m['destination']}"
        by_pair[key].append(m["latency_ms"])
    results = []
    for pair, latencies in sorted(by_pair.items()):
        s = sorted(latencies)
        n = len(s)
        src, dst = pair.split("→")
        results.append({"source": src, "destination": dst, "samples": n,
                        "avg_ms": round(sum(s) / n, 1), "p50_ms": s[n // 2],
                        "p99_ms": s[int(n * 0.99)], "min_ms": s[0], "max_ms": s[-1]})
    return {"pairs": results, "total_pairs": len(results),
            "total_measurements": len(measurements)}

"""Network latency mapper — measure inter-service latency."""
from __future__ import annotations


def measure_latency(measurements: list[dict]) -> dict:
    pairs: dict[str, list[float]] = {}
    for m in measurements:
        key = f"{m['from']}→{m['to']}"
        pairs.setdefault(key, []).append(m.get("latency_ms", 0))
    results = []
    for pair, latencies in pairs.items():
        s = sorted(latencies)
        avg = round(sum(s) / len(s), 1)
        p99 = s[int(len(s) * 0.99)] if len(s) >= 2 else s[-1]
        results.append({"pair": pair, "avg_ms": avg, "p99_ms": p99,
                         "min_ms": s[0], "max_ms": s[-1], "samples": len(s)})
    results.sort(key=lambda r: -r["avg_ms"])
    return {"pairs": results, "total_pairs": len(results),
            "total_measurements": len(measurements),
            "highest_latency": results[0]["pair"] if results else None}

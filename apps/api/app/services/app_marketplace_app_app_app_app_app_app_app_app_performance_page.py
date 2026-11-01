"""Performance page — app performance metrics and Web Vitals."""


def build_performance_page(*, metrics: dict, budget: dict | None = None) -> dict:
    lcp = metrics.get("lcp_ms", 0)
    fid = metrics.get("fid_ms", 0)
    cls = metrics.get("cls", 0)
    ttfb = metrics.get("ttfb_ms", 0)

    def _score(val: float, good: float, poor: float) -> str:
        return "good" if val <= good else "needs_improvement" if val <= poor else "poor"

    vitals = [
        {"name": "LCP", "value": lcp, "display": f"{lcp}ms", "threshold": "≤2500ms",
         "score": _score(lcp, 2500, 4000), "description": "Largest Contentful Paint"},
        {"name": "FID", "value": fid, "display": f"{fid}ms", "threshold": "≤100ms",
         "score": _score(fid, 100, 300), "description": "First Input Delay"},
        {"name": "CLS", "value": cls, "display": f"{cls:.3f}", "threshold": "≤0.1",
         "score": _score(cls, 0.1, 0.25), "description": "Cumulative Layout Shift"},
        {"name": "TTFB", "value": ttfb, "display": f"{ttfb}ms", "threshold": "≤800ms",
         "score": _score(ttfb, 800, 1800), "description": "Time to First Byte"},
    ]
    overall = "good" if all(v["score"] == "good" for v in vitals) else \
              "poor" if any(v["score"] == "poor" for v in vitals) else "needs_improvement"
    return {"vitals": vitals, "overall": overall,
            "overall_label": {"good": "✅ Good", "needs_improvement": "🟡 Needs Work", "poor": "🔴 Poor"}.get(overall, "")}

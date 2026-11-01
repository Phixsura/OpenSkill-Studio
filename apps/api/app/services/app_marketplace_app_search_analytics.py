"""Search analytics — track and report marketplace search behavior."""


def analyze_search_queries(*, queries: list[dict]) -> dict:
    term_counts: dict[str, int] = {}
    zero_results: list[str] = []
    total_clicks = 0
    total_results = 0
    for q in queries:
        term = q.get("query", "").lower().strip()
        term_counts[term] = term_counts.get(term, 0) + 1
        if q.get("results_count", 0) == 0:
            zero_results.append(term)
        total_clicks += q.get("click_count", 0)
        total_results += q.get("results_count", 0)
    top_queries = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    unique_zero = sorted(set(zero_results))
    ctr = round(total_clicks / max(len(queries), 1) * 100, 1)
    return {
        "total_searches": len(queries),
        "unique_queries": len(term_counts),
        "top_queries": [{"query": q, "count": c} for q, c in top_queries],
        "zero_result_queries": unique_zero[:10],
        "zero_result_rate": round(len(zero_results) / max(len(queries), 1) * 100, 1),
        "avg_results_per_query": round(total_results / max(len(queries), 1), 1),
        "click_through_rate": ctr,
    }

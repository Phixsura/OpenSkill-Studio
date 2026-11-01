"""Metric explorer — search and browse platform metrics."""
from __future__ import annotations


METRIC_CATALOG = [
    {"name": "http_requests_total", "type": "counter", "unit": "requests", "labels": ["method", "status"]},
    {"name": "http_request_duration_seconds", "type": "histogram", "unit": "seconds", "labels": ["method", "path"]},
    {"name": "process_cpu_seconds_total", "type": "counter", "unit": "seconds", "labels": ["service"]},
    {"name": "process_resident_memory_bytes", "type": "gauge", "unit": "bytes", "labels": ["service"]},
    {"name": "db_connections_active", "type": "gauge", "unit": "connections", "labels": ["pool"]},
    {"name": "cache_hit_ratio", "type": "gauge", "unit": "ratio", "labels": ["cache"]},
    {"name": "queue_depth", "type": "gauge", "unit": "messages", "labels": ["queue"]},
    {"name": "error_rate", "type": "gauge", "unit": "percent", "labels": ["service"]},
]


def search_metrics(query: str, metric_type: str | None = None) -> dict:
    q = query.lower()
    results = [m for m in METRIC_CATALOG
               if q in m["name"].lower() or any(q in l.lower() for l in m["labels"])]
    if metric_type:
        results = [m for m in results if m["type"] == metric_type]
    return {"results": results, "total": len(results), "query": query}


def metric_catalog_summary() -> dict:
    by_type: dict[str, int] = {}
    for m in METRIC_CATALOG:
        by_type[m["type"]] = by_type.get(m["type"], 0) + 1
    return {"total_metrics": len(METRIC_CATALOG), "by_type": by_type,
            "types": sorted(by_type.keys())}

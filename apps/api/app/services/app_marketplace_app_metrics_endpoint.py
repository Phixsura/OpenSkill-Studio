"""Metrics endpoint — Prometheus-compatible metrics."""
def get_metrics() -> dict:
    return {"http_requests_total": 1500000, "http_request_duration_seconds": 0.045,
            "active_connections": 250, "app_installs_total": 25000}

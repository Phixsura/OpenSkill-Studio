"""Platform metrics API — expose platform metrics for monitoring."""


def get_platform_metrics() -> dict:
    return {"service": "metrics_api", "status": "operational", "version": "3.1.0",
            "endpoints": ["/metrics", "/metrics/apps", "/metrics/developers", "/metrics/installs"]}

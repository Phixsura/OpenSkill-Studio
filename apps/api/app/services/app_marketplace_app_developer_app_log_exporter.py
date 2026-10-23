"""Log exporter — export app logs to external observability platforms."""

SUPPORTED_DESTINATIONS = {
    "datadog": {"format": "json", "protocol": "https", "batch_size": 1000},
    "splunk": {"format": "hec", "protocol": "https", "batch_size": 500},
    "elasticsearch": {"format": "json", "protocol": "https", "batch_size": 200},
    "cloudwatch": {"format": "json", "protocol": "aws", "batch_size": 1000},
    "grafana_loki": {"format": "logfmt", "protocol": "https", "batch_size": 500},
}


def create_export_config(*, destination: str, endpoint_url: str, api_key: str,
                            filters: list[str] | None = None) -> dict:
    if destination not in SUPPORTED_DESTINATIONS:
        return {"error": f"Unsupported destination. Use: {', '.join(sorted(SUPPORTED_DESTINATIONS))}"}
    dest_config = SUPPORTED_DESTINATIONS[destination]
    return {"destination": destination, "endpoint_url": endpoint_url,
            "has_api_key": bool(api_key), "filters": filters or ["*"],
            "format": dest_config["format"], "batch_size": dest_config["batch_size"],
            "status": "configured", "error": None}


def format_log_batch(*, logs: list[dict], format: str) -> list[str]:
    formatted = []
    for log in logs:
        if format == "json":
            import json
            formatted.append(json.dumps(log, default=str))
        elif format == "logfmt":
            parts = [f'{k}="{v}"' for k, v in log.items()]
            formatted.append(" ".join(parts))
        else:
            formatted.append(str(log))
    return formatted


def get_export_stats(*, exports: list[dict]) -> dict:
    total_logs = sum(e.get("log_count", 0) for e in exports)
    successful = sum(1 for e in exports if e.get("status") == "success")
    return {"total_exports": len(exports), "total_logs": total_logs,
            "success_rate": round(successful / max(len(exports), 1) * 100, 1)}

"""Fleet metrics-server — track resource metrics pipeline."""
from __future__ import annotations
def fleet_metrics_server(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    nodes_scraped = sum(i.get("nodes_scraped", 0) for i in instances)
    scrape_interval = min((i.get("scrape_interval_sec", 60) for i in instances), default=60)
    return {"instances": len(instances), "healthy": len(healthy), "nodes_scraped": nodes_scraped,
            "scrape_interval_sec": scrape_interval, "all_healthy": len(healthy) == len(instances)}

"""Service discovery — register and discover microservices."""

import secrets
from datetime import datetime, timedelta


def register_service(*, service_name: str, host: str, port: int,
                       tags: list[str] | None = None, health_url: str | None = None) -> dict:
    if port < 1 or port > 65535:
        return {"error": "Port must be 1-65535"}
    instance_id = f"{service_name}-{secrets.token_hex(4)}"
    return {
        "instance_id": instance_id,
        "service_name": service_name,
        "address": f"{host}:{port}",
        "tags": tags or [],
        "health_check_url": health_url or f"http://{host}:{port}/health",
        "status": "healthy",
        "registered_at": datetime.utcnow().isoformat(),
        "ttl_sec": 30,
    }


def discover_service(*, service_name: str, instances: list[dict],
                       strategy: str = "round_robin") -> dict:
    healthy = [i for i in instances if i.get("status") == "healthy"]
    if not healthy:
        return {"error": f"No healthy instances for {service_name}"}
    if strategy == "round_robin":
        selected = healthy[0]
    elif strategy == "random":
        import random
        selected = random.choice(healthy)
    else:
        selected = healthy[0]
    return {
        "service_name": service_name,
        "selected": selected,
        "strategy": strategy,
        "healthy_count": len(healthy),
        "total_instances": len(instances),
    }

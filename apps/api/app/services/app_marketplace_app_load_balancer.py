"""Load balancer — distribute requests across app instances."""

import hashlib


def round_robin(*, instances: list[dict], request_index: int) -> dict | None:
    if not instances:
        return None
    healthy = [i for i in instances if i.get("status") == "healthy"]
    if not healthy:
        return None
    return healthy[request_index % len(healthy)]


def consistent_hash(*, key: str, instances: list[dict]) -> dict | None:
    healthy = [i for i in instances if i.get("status") == "healthy"]
    if not healthy:
        return None
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return healthy[h % len(healthy)]


def get_instance_weights(*, instances: list[dict]) -> list[dict]:
    total_capacity = sum(i.get("capacity", 1) for i in instances)
    return [{"id": i["id"], "weight_pct": round(i.get("capacity", 1) / max(total_capacity, 1) * 100, 1),
             "status": i.get("status")} for i in instances]


def health_check_summary(*, instances: list[dict]) -> dict:
    healthy = sum(1 for i in instances if i.get("status") == "healthy")
    return {"total": len(instances), "healthy": healthy, "unhealthy": len(instances) - healthy,
            "availability_pct": round(healthy / max(len(instances), 1) * 100, 1)}

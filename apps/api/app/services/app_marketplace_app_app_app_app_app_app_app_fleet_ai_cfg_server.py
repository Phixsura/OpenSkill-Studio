"""Fleet AI Config Server — track centralized AI configuration distribution."""
from __future__ import annotations
def fleet_ai_config_server(servers: list[dict]) -> dict:
    active = [s for s in servers if s.get("active", True)]
    configs = sum(s.get("configs", 0) for s in servers)
    clients = sum(s.get("clients", 0) for s in servers)
    updates_24h = sum(s.get("updates_24h", 0) for s in servers)
    return {"servers": len(servers), "active": len(active), "configs": configs,
            "clients": clients, "updates_24h": updates_24h, "serving": clients > 0}

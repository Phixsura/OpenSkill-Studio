"""Fleet Azure Service Bus — track message broker health."""
from __future__ import annotations
def fleet_servicebus_status(namespaces: list[dict]) -> dict:
    active = [n for n in namespaces if n.get("status") == "Active"]
    total_msgs = sum(n.get("messages_24h", 0) for n in namespaces)
    dlq_msgs = sum(n.get("dlq_count", 0) for n in namespaces)
    return {"namespaces": len(namespaces), "active": len(active), "messages_24h": total_msgs,
            "dlq_count": dlq_msgs, "healthy": dlq_msgs == 0}

"""Fleet RabbitMQ — track message broker health."""
from __future__ import annotations
def fleet_rabbitmq_status(nodes: list[dict]) -> dict:
    running = [n for n in nodes if n.get("running", True)]
    total_queues = sum(n.get("queues", 0) for n in nodes)
    total_msgs = sum(n.get("messages", 0) for n in nodes)
    return {"nodes": len(nodes), "running": len(running), "queues": total_queues,
            "messages": total_msgs, "healthy": len(running) == len(nodes)}

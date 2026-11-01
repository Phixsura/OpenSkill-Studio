"""Fleet Kafka — track Kafka cluster health."""
from __future__ import annotations
def fleet_kafka_status(brokers: list[dict]) -> dict:
    online = [b for b in brokers if b.get("online", True)]
    under_replicated = sum(b.get("under_replicated_partitions", 0) for b in brokers)
    total_topics = sum(b.get("topics", 0) for b in brokers)
    return {"brokers": len(brokers), "online": len(online), "under_replicated": under_replicated,
            "total_topics": total_topics, "healthy": len(online) == len(brokers) and under_replicated == 0}

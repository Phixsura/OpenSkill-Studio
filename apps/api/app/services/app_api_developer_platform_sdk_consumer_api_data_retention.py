"""Consumer Data Retention — data retention policy management with purge scheduling."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

DATA_CATEGORIES = ("logs", "analytics", "audit", "requests", "responses", "user_data")


@dataclass
class RetentionPolicy:
    category: str
    retention_days: int
    auto_purge: bool = True
    archive_before_purge: bool = False


@dataclass
class PurgeRecord:
    category: str
    purged_at: str
    records_purged: int
    archived: bool


@dataclass
class DataRetentionManager:
    """Manage data retention policies and purge scheduling."""

    _policies: dict[str, dict[str, RetentionPolicy]] = field(default_factory=dict)  # consumer -> {category: policy}
    _purge_history: list[PurgeRecord] = field(default_factory=list)

    def set_policy(self, consumer_id: str, category: str, retention_days: int,
                   auto_purge: bool = True, archive_before_purge: bool = False) -> dict:
        if category not in DATA_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        if retention_days < 1:
            raise ValueError("retention_days must be positive")
        policies = self._policies.setdefault(consumer_id, {})
        policies[category] = RetentionPolicy(
            category=category, retention_days=retention_days,
            auto_purge=auto_purge, archive_before_purge=archive_before_purge,
        )
        logger.info("retention_policy_set", consumer_id=consumer_id,
                     category=category, days=retention_days)
        return {"consumer_id": consumer_id, "category": category,
                "retention_days": retention_days}

    def get_policies(self, consumer_id: str) -> list[dict]:
        policies = self._policies.get(consumer_id, {})
        results = []
        for cat in DATA_CATEGORIES:
            policy = policies.get(cat)
            if policy:
                results.append({
                    "category": cat, "retention_days": policy.retention_days,
                    "auto_purge": policy.auto_purge,
                    "archive_before_purge": policy.archive_before_purge,
                })
            else:
                results.append({"category": cat, "retention_days": None, "status": "no_policy"})
        return results

    def execute_purge(self, consumer_id: str, category: str,
                      current_date: str, records_found: int) -> dict:
        policies = self._policies.get(consumer_id, {})
        policy = policies.get(category)
        if not policy:
            return {"purged": False, "reason": "no_policy"}
        archived = policy.archive_before_purge
        record = PurgeRecord(
            category=category, purged_at=current_date,
            records_purged=records_found, archived=archived,
        )
        self._purge_history.append(record)
        logger.info("purge_executed", consumer_id=consumer_id,
                     category=category, records=records_found)
        return {"purged": True, "records_purged": records_found,
                "archived": archived, "category": category}

    def get_due_purges(self, consumer_id: str, current_day: int = 0) -> list[dict]:
        """Get categories that need purging (simplified: checks auto_purge flag)."""
        policies = self._policies.get(consumer_id, {})
        due = []
        for cat, policy in policies.items():
            if policy.auto_purge:
                due.append({
                    "category": cat,
                    "retention_days": policy.retention_days,
                    "archive_first": policy.archive_before_purge,
                })
        return due

    def get_purge_history(self, limit: int = 20) -> list[dict]:
        return [
            {"category": r.category, "purged_at": r.purged_at,
             "records_purged": r.records_purged, "archived": r.archived}
            for r in self._purge_history[-limit:]
        ]

    def remove_policy(self, consumer_id: str, category: str) -> dict:
        policies = self._policies.get(consumer_id, {})
        if category in policies:
            del policies[category]
            return {"removed": True}
        return {"removed": False}

    def get_stats(self) -> dict:
        total_policies = sum(len(p) for p in self._policies.values())
        total_purged = sum(r.records_purged for r in self._purge_history)
        return {
            "consumers_with_policies": len(self._policies),
            "total_policies": total_policies,
            "total_purges": len(self._purge_history),
            "total_records_purged": total_purged,
        }

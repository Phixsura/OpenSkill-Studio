"""Endpoint Traffic Shaper — traffic shaping with priority lanes."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

PRIORITIES = ("critical", "high", "normal", "low", "background")


@dataclass
class TrafficRule:
    rule_id: str
    consumer_id: str
    priority: str
    max_rps: int
    current_rps: int = 0
    throttled_count: int = 0


@dataclass
class TrafficShaper:
    """Shape traffic with priority-based lanes and throttling."""

    _rules: dict[str, TrafficRule] = field(default_factory=dict)  # consumer_id -> rule
    _global_max_rps: int = 10000
    _global_current_rps: int = 0

    def configure_global(self, max_rps: int) -> dict:
        if max_rps < 1:
            raise ValueError("max_rps must be positive")
        self._global_max_rps = max_rps
        return {"global_max_rps": max_rps}

    def set_rule(self, rule: TrafficRule) -> dict:
        if rule.priority not in PRIORITIES:
            raise ValueError(f"Invalid priority: {rule.priority}")
        if rule.max_rps < 1:
            raise ValueError("max_rps must be positive")
        self._rules[rule.consumer_id] = rule
        logger.info("traffic_rule_set", consumer_id=rule.consumer_id, priority=rule.priority)
        return {"consumer_id": rule.consumer_id, "priority": rule.priority, "max_rps": rule.max_rps}

    def admit(self, consumer_id: str) -> dict:
        rule = self._rules.get(consumer_id)
        if not rule:
            # Default: normal priority, no per-consumer limit
            if self._global_current_rps >= self._global_max_rps:
                return {"admitted": False, "reason": "global_limit"}
            self._global_current_rps += 1
            return {"admitted": True, "priority": "normal"}

        # Check per-consumer limit
        if rule.current_rps >= rule.max_rps:
            rule.throttled_count += 1
            return {"admitted": False, "reason": "consumer_limit",
                    "priority": rule.priority, "throttled_total": rule.throttled_count}

        # Check global limit with priority bypass for critical
        if self._global_current_rps >= self._global_max_rps:
            if rule.priority == "critical":
                # Critical bypasses global limit
                rule.current_rps += 1
                self._global_current_rps += 1
                return {"admitted": True, "priority": "critical", "bypassed_global": True}
            rule.throttled_count += 1
            return {"admitted": False, "reason": "global_limit", "priority": rule.priority}

        rule.current_rps += 1
        self._global_current_rps += 1
        return {"admitted": True, "priority": rule.priority}

    def reset_window(self) -> dict:
        self._global_current_rps = 0
        for rule in self._rules.values():
            rule.current_rps = 0
        return {"reset": True, "consumers": len(self._rules)}

    def get_consumer_status(self, consumer_id: str) -> dict:
        rule = self._rules.get(consumer_id)
        if not rule:
            return {"consumer_id": consumer_id, "status": "no_rule"}
        usage_pct = round(rule.current_rps / rule.max_rps * 100, 1)
        return {
            "consumer_id": consumer_id,
            "priority": rule.priority,
            "current_rps": rule.current_rps,
            "max_rps": rule.max_rps,
            "usage_pct": usage_pct,
            "throttled_count": rule.throttled_count,
            "status": "throttled" if rule.current_rps >= rule.max_rps else "flowing",
        }

    def get_overview(self) -> dict:
        rules = list(self._rules.values())
        by_priority = {}
        for p in PRIORITIES:
            by_priority[p] = sum(1 for r in rules if r.priority == p)
        total_throttled = sum(r.throttled_count for r in rules)
        return {
            "global_rps": f"{self._global_current_rps}/{self._global_max_rps}",
            "consumers": len(rules),
            "by_priority": by_priority,
            "total_throttled": total_throttled,
        }

    def list_rules(self) -> list[dict]:
        return [self.get_consumer_status(r.consumer_id) for r in self._rules.values()]

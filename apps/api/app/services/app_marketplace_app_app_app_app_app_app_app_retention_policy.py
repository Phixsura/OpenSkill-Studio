"""Data retention policy manager — enforce data lifecycle and deletion schedules."""
from __future__ import annotations


class RetentionPolicyManager:
    def __init__(self):
        self._policies: dict[str, dict] = {}

    def add_policy(self, *, resource: str, retention_days: int,
                    action: str = "delete", archive_before: bool = False) -> dict:
        self._policies[resource] = {
            "resource": resource, "retention_days": retention_days,
            "action": action, "archive_before": archive_before,
        }
        return {"resource": resource, "retention_days": retention_days, "action": action}

    def check_compliance(self, records: list[dict], *, now_days: int = 0) -> dict:
        compliant = 0
        violations = []
        for r in records:
            resource = r.get("resource", "")
            age_days = r.get("age_days", 0)
            policy = self._policies.get(resource)
            if not policy:
                continue
            if age_days > policy["retention_days"]:
                violations.append({"resource": resource, "record_id": r.get("id", ""),
                                    "age_days": age_days, "max_days": policy["retention_days"],
                                    "overdue_days": age_days - policy["retention_days"]})
            else:
                compliant += 1
        return {"total_checked": len(records), "compliant": compliant,
                "violations": violations, "violation_count": len(violations),
                "all_compliant": len(violations) == 0}

    def summary(self) -> dict:
        return {"total_policies": len(self._policies),
                "policies": [{"resource": p["resource"], "retention_days": p["retention_days"],
                              "action": p["action"], "archive": p["archive_before"]}
                             for p in self._policies.values()]}

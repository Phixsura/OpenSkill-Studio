"""Auto-remediation engine — automatically fix common platform issues."""
from __future__ import annotations


class AutoRemediation:
    def __init__(self):
        self._rules: list[dict] = []
        self._actions_taken: list[dict] = []

    def add_rule(self, name: str, condition: callable, action: callable, severity: str = "warning") -> dict:
        self._rules.append({"name": name, "condition": condition, "action": action, "severity": severity})
        return {"name": name, "added": True, "total_rules": len(self._rules)}

    def evaluate(self, context: dict) -> dict:
        triggered = []
        for rule in self._rules:
            if rule["condition"](context):
                result = rule["action"](context)
                entry = {"rule": rule["name"], "severity": rule["severity"],
                         "action_result": result, "auto_fixed": True}
                triggered.append(entry)
                self._actions_taken.append(entry)
        return {"evaluated": len(self._rules), "triggered": len(triggered),
                "actions": triggered}

    def history(self, limit: int = 20) -> list[dict]:
        return self._actions_taken[-limit:]

    def stats(self) -> dict:
        by_severity = {}
        for a in self._actions_taken:
            by_severity[a["severity"]] = by_severity.get(a["severity"], 0) + 1
        return {"total_rules": len(self._rules), "actions_taken": len(self._actions_taken),
                "by_severity": by_severity}

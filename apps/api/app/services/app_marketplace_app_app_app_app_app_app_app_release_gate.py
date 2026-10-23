"""Release gating engine — enforce quality gates before release."""
from __future__ import annotations


def create_gate(name: str, checks: list[dict]) -> dict:
    items = []
    for c in checks:
        items.append({"name": c["name"], "type": c.get("type", "required"),
                       "status": "pending", "result": None})
    return {"name": name, "checks": items, "total": len(items), "passed": 0, "failed": 0}


def evaluate_gate(gate: dict, results: dict[str, bool]) -> dict:
    passed = 0
    failed = 0
    blocking = False
    for check in gate["checks"]:
        result = results.get(check["name"])
        if result is True:
            check["status"] = "passed"
            check["result"] = True
            passed += 1
        elif result is False:
            check["status"] = "failed"
            check["result"] = False
            failed += 1
            if check["type"] == "required":
                blocking = True
    gate["passed"] = passed
    gate["failed"] = failed
    can_release = not blocking and passed + failed == gate["total"]
    return {"gate": gate["name"], "passed": passed, "failed": failed,
            "total": gate["total"], "can_release": can_release, "blocking": blocking}

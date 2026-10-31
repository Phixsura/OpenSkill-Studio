"""Release gate — pre-release quality gates that must pass before deploy."""


GATE_TYPES = {
    "tests": {"label": "Test Suite", "icon": "🧪", "required": True},
    "security_scan": {"label": "Security Scan", "icon": "🔒", "required": True},
    "performance": {"label": "Performance Budget", "icon": "⚡", "required": False},
    "code_review": {"label": "Code Review", "icon": "👀", "required": True},
    "staging_deploy": {"label": "Staging Deploy", "icon": "🧪", "required": True},
    "smoke_test": {"label": "Smoke Test", "icon": "💨", "required": True},
    "changelog": {"label": "Changelog Updated", "icon": "📝", "required": False},
}


def evaluate_gates(*, results: dict[str, bool]) -> dict:
    gates = []
    for gate_id, meta in GATE_TYPES.items():
        passed = results.get(gate_id, False)
        gates.append({
            "id": gate_id, **meta,
            "passed": passed,
            "status": "pass" if passed else ("fail" if meta["required"] else "skip"),
        })
    required_passed = all(g["passed"] for g in gates if g["required"])
    total_passed = sum(1 for g in gates if g["passed"])
    return {
        "gates": gates,
        "total": len(gates),
        "passed": total_passed,
        "release_ready": required_passed,
        "blocking": [g["id"] for g in gates if g["required"] and not g["passed"]],
    }

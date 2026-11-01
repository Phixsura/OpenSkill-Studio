"""Automation page builder — compile automation rules page data."""

def build_automations_page(*, rules: list[dict], max_rules: int = 25) -> dict:
    active = [r for r in rules if r.get("enabled", True)]
    return {"rules": rules, "total": len(rules), "active": len(active), "disabled": len(rules) - len(active),
            "max": max_rules, "can_add": len(rules) < max_rules}

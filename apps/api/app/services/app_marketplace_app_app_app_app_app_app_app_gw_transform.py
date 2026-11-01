"""Gateway request transformer — transform requests at the gateway."""
from __future__ import annotations
import html


def transform_request(request: dict, rules: list[dict]) -> dict:
    result = dict(request)
    applied = []
    for rule in rules:
        action = rule["action"]
        if action == "add_header":
            result.setdefault("headers", {})[rule["key"]] = rule["value"]
            applied.append(f"add_header:{rule['key']}")
        elif action == "remove_header":
            result.get("headers", {}).pop(rule["key"], None)
            applied.append(f"remove_header:{rule['key']}")
        elif action == "rewrite_path":
            if result.get("path", "").startswith(rule["from"]):
                result["path"] = result["path"].replace(rule["from"], rule["to"], 1)
                applied.append(f"rewrite:{rule['from']}→{rule['to']}")
        elif action == "set_timeout":
            result["timeout_ms"] = rule["value"]
            applied.append(f"timeout:{rule['value']}ms")
    return {"request": result, "rules_applied": applied, "count": len(applied)}

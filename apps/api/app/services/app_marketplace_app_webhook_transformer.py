"""Webhook transformer — transform webhook payloads before delivery."""

import json
import copy


def apply_transform(*, payload: dict, rules: list[dict]) -> dict:
    result = copy.deepcopy(payload)
    applied = []
    for rule in rules:
        action = rule.get("action")
        path = rule.get("path", "")
        if action == "rename" and path in result:
            result[rule["to"]] = result.pop(path)
            applied.append(f"renamed {path} → {rule['to']}")
        elif action == "remove" and path in result:
            del result[path]
            applied.append(f"removed {path}")
        elif action == "add":
            result[path] = rule.get("value")
            applied.append(f"added {path}")
        elif action == "mask" and path in result:
            val = str(result[path])
            result[path] = val[:2] + "•" * max(len(val) - 4, 0) + val[-2:] if len(val) > 4 else "••••"
            applied.append(f"masked {path}")
    return {"transformed": result, "rules_applied": len(applied),
            "changes": applied}


def validate_transform_rules(*, rules: list[dict]) -> dict:
    valid_actions = {"rename", "remove", "add", "mask"}
    errors = []
    for i, rule in enumerate(rules):
        if rule.get("action") not in valid_actions:
            errors.append(f"Rule {i}: invalid action '{rule.get('action')}'")
        if not rule.get("path"):
            errors.append(f"Rule {i}: missing path")
        if rule.get("action") == "rename" and not rule.get("to"):
            errors.append(f"Rule {i}: rename requires 'to' field")
    return {"valid": len(errors) == 0, "errors": errors}

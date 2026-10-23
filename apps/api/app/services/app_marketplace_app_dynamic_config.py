"""Dynamic config — runtime-changeable configuration without redeployment."""

from datetime import datetime


def create_config_entry(*, key: str, value: str, value_type: str = "string",
                          description: str = "", environment: str = "all") -> dict:
    valid_types = {"string", "number", "boolean", "json"}
    if value_type not in valid_types:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(valid_types))}"}
    parsed = value
    if value_type == "number":
        try:
            parsed = float(value)
        except ValueError:
            return {"error": f"Cannot parse '{value}' as number"}
    elif value_type == "boolean":
        parsed = value.lower() in ("true", "1", "yes")
    return {
        "key": key,
        "value": parsed,
        "raw_value": value,
        "value_type": value_type,
        "description": description,
        "environment": environment,
        "updated_at": datetime.utcnow().isoformat(),
    }


def get_config_snapshot(*, configs: list[dict], environment: str = "production") -> dict:
    filtered = [c for c in configs if c.get("environment") in (environment, "all")]
    snapshot = {c["key"]: c["value"] for c in filtered}
    return {
        "environment": environment,
        "config": snapshot,
        "total_keys": len(snapshot),
        "generated_at": datetime.utcnow().isoformat(),
    }

"""Webhook transform — transform webhook payloads before delivery."""


def apply_transform(*, payload: dict, mappings: list[dict]) -> dict:
    result = {}
    for m in mappings:
        source = m.get("source", "")
        target = m.get("target", source)
        value = payload
        for key in source.split("."):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break
        if value is not None:
            result[target] = value
    return result


def build_transform_preview(*, payload: dict, mappings: list[dict]) -> dict:
    transformed = apply_transform(payload=payload, mappings=mappings)
    return {"original": payload, "transformed": transformed,
            "fields_mapped": len(transformed), "fields_dropped": len(payload) - len(transformed)}


def validate_mappings(*, mappings: list[dict]) -> dict:
    errors = []
    for i, m in enumerate(mappings):
        if not m.get("source"):
            errors.append(f"Mapping {i}: missing source")
        if not m.get("target"):
            errors.append(f"Mapping {i}: missing target")
    return {"valid": len(errors) == 0, "errors": errors}

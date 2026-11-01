"""Version diff checker — compare API responses between versions."""


def compare_responses(*, v1_response: dict, v2_response: dict) -> dict:
    v1_keys = set(v1_response.keys())
    v2_keys = set(v2_response.keys())
    added = sorted(v2_keys - v1_keys)
    removed = sorted(v1_keys - v2_keys)
    modified = []
    for key in sorted(v1_keys & v2_keys):
        if v1_response[key] != v2_response[key]:
            old_type = type(v1_response[key]).__name__
            new_type = type(v2_response[key]).__name__
            modified.append({"field": key, "old_type": old_type, "new_type": new_type,
                              "type_changed": old_type != new_type})
    breaking = len(removed) > 0 or any(m["type_changed"] for m in modified)
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "total_changes": len(added) + len(removed) + len(modified),
        "breaking": breaking,
        "compatible": not breaking,
    }

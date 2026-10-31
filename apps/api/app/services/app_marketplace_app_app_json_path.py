"""JSON path — simple JSONPath query engine."""

import html
import re


def query_json(*, data: dict | list, path: str) -> dict:
    parts = [p for p in path.replace("$.", "").split(".") if p]
    current = data
    traversed = []
    for part in parts:
        # Handle array index: items[0]
        m = re.match(r"(\w+)\[(\d+)\]", part)
        if m:
            key, idx = m.group(1), int(m.group(2))
            if isinstance(current, dict) and key in current:
                current = current[key]
                traversed.append(key)
                if isinstance(current, list) and idx < len(current):
                    current = current[idx]
                    traversed.append(f"[{idx}]")
                else:
                    return {"found": False, "path": path, "error": f"Index {idx} out of range"}
            else:
                return {"found": False, "path": path, "error": f"Key '{key}' not found"}
        elif isinstance(current, dict) and part in current:
            current = current[part]
            traversed.append(part)
        else:
            return {"found": False, "path": path, "error": f"Key '{part}' not found"}
    return {"found": True, "path": path, "value": current,
            "type": type(current).__name__, "traversed": traversed}

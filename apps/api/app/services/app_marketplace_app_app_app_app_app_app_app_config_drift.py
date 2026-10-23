"""Config drift detector — compare expected vs actual infrastructure config."""
from __future__ import annotations


def detect_drift(expected: dict, actual: dict, *, path: str = "") -> list[dict]:
    diffs = []
    all_keys = set(list(expected.keys()) + list(actual.keys()))
    for key in sorted(all_keys):
        full_path = f"{path}.{key}" if path else key
        if key not in actual:
            diffs.append({"path": full_path, "type": "missing", "expected": expected[key], "actual": None})
        elif key not in expected:
            diffs.append({"path": full_path, "type": "extra", "expected": None, "actual": actual[key]})
        elif isinstance(expected[key], dict) and isinstance(actual[key], dict):
            diffs.extend(detect_drift(expected[key], actual[key], path=full_path))
        elif expected[key] != actual[key]:
            diffs.append({"path": full_path, "type": "changed", "expected": expected[key], "actual": actual[key]})
    return diffs


def summarize_drift(diffs: list[dict]) -> dict:
    by_type = {"missing": 0, "extra": 0, "changed": 0}
    for d in diffs:
        by_type[d["type"]] = by_type.get(d["type"], 0) + 1
    return {
        "total_drifts": len(diffs), "by_type": by_type,
        "has_drift": len(diffs) > 0,
        "severity": "critical" if by_type["missing"] > 0 else "warning" if diffs else "clean",
        "diffs": diffs,
    }

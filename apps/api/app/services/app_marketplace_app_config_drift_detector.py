"""Config drift detector — detect configuration differences between environments."""


def detect_drift(*, expected: dict, actual: dict) -> dict:
    drifts = []
    all_keys = set(expected.keys()) | set(actual.keys())
    for key in sorted(all_keys):
        exp = expected.get(key)
        act = actual.get(key)
        if exp != act:
            drifts.append({"key": key, "expected": exp, "actual": act,
                           "type": "missing" if act is None else "extra" if exp is None else "changed"})
    return {"has_drift": len(drifts) > 0, "drifts": drifts, "drift_count": len(drifts),
            "total_keys": len(all_keys)}


def auto_remediate(*, drifts: list[dict], policy: str = "reset") -> dict:
    actions = []
    for d in drifts:
        if policy == "reset":
            actions.append({"key": d["key"], "action": "set", "value": d["expected"]})
        elif policy == "alert":
            actions.append({"key": d["key"], "action": "alert", "value": None})
    return {"actions": actions, "policy": policy}

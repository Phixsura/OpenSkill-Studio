"""Config drift detector — detect configuration drift across environments."""
from __future__ import annotations


def detect_drift(expected: dict[str, str], actual: dict[str, str]) -> dict:
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = []
    for k in sorted(set(expected) & set(actual)):
        if expected[k] != actual[k]:
            changed.append({"key": k, "expected": expected[k], "actual": actual[k]})
    drifted = len(missing) + len(extra) + len(changed) > 0
    severity = "critical" if missing else ("warning" if changed else ("info" if extra else "ok"))
    return {"drifted": drifted, "severity": severity, "missing": missing,
            "extra": extra, "changed": changed,
            "total_issues": len(missing) + len(extra) + len(changed)}


def compare_envs(envs: dict[str, dict[str, str]], baseline: str) -> dict:
    base = envs.get(baseline, {})
    results = {}
    for name, cfg in envs.items():
        if name == baseline:
            continue
        results[name] = detect_drift(base, cfg)
    drifted_count = sum(1 for r in results.values() if r["drifted"])
    return {"baseline": baseline, "comparisons": results,
            "total_envs": len(envs) - 1, "drifted": drifted_count}

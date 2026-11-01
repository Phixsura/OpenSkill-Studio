"""Service mesh golden path — define and track the ideal request path."""
from __future__ import annotations


def define_golden_path(steps: list[str]) -> dict:
    return {"path": steps, "length": len(steps),
            "entry": steps[0] if steps else "", "exit": steps[-1] if steps else ""}


def check_against_golden(actual_path: list[str], golden: list[str]) -> dict:
    deviations = []
    for i, step in enumerate(actual_path):
        if i < len(golden) and step != golden[i]:
            deviations.append({"position": i, "expected": golden[i], "actual": step})
    extra = actual_path[len(golden):] if len(actual_path) > len(golden) else []
    missing = golden[len(actual_path):] if len(golden) > len(actual_path) else []
    follows_golden = len(deviations) == 0 and not extra and not missing
    return {"follows_golden": follows_golden, "deviations": deviations,
            "extra_hops": extra, "missing_hops": missing,
            "actual_length": len(actual_path), "golden_length": len(golden)}

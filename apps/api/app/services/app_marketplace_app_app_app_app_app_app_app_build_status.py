"""Build status tracker — monitor CI build health across repos."""
from __future__ import annotations


def track_builds(builds: list[dict]) -> dict:
    passed = sum(1 for b in builds if b.get("status") == "passed")
    failed = sum(1 for b in builds if b.get("status") == "failed")
    running = sum(1 for b in builds if b.get("status") == "running")
    durations = [b.get("duration_sec", 0) for b in builds if b.get("duration_sec")]
    avg_duration = round(sum(durations) / max(len(durations), 1))
    pass_rate = round(passed / max(passed + failed, 1) * 100)
    return {"total": len(builds), "passed": passed, "failed": failed,
            "running": running, "pass_rate": pass_rate,
            "avg_duration_sec": avg_duration,
            "health": "green" if pass_rate >= 95 else "yellow" if pass_rate >= 80 else "red"}


def flaky_tests(builds: list[dict]) -> list[dict]:
    test_results: dict[str, dict] = {}
    for b in builds:
        for t in b.get("tests", []):
            name = t.get("name", "")
            if name not in test_results:
                test_results[name] = {"name": name, "passes": 0, "failures": 0}
            if t.get("passed"):
                test_results[name]["passes"] += 1
            else:
                test_results[name]["failures"] += 1
    flaky = []
    for t in test_results.values():
        total = t["passes"] + t["failures"]
        if total >= 3 and t["failures"] > 0 and t["passes"] > 0:
            flaky.append({**t, "flake_rate": round(t["failures"] / total * 100, 1)})
    return sorted(flaky, key=lambda t: -t["flake_rate"])

"""Service readiness gate — check if all dependencies are ready before serving."""
from __future__ import annotations


class ReadinessGate:
    def __init__(self):
        self._checks: dict[str, dict] = {}

    def register_check(self, name: str, check_fn: callable, critical: bool = True) -> dict:
        self._checks[name] = {"fn": check_fn, "critical": critical, "last_result": None}
        return {"name": name, "critical": critical}

    def evaluate(self) -> dict:
        results = []
        for name, check in self._checks.items():
            try:
                ok = check["fn"]()
                results.append({"name": name, "ready": bool(ok), "critical": check["critical"]})
                check["last_result"] = bool(ok)
            except Exception as e:
                results.append({"name": name, "ready": False, "critical": check["critical"], "error": str(e)})
                check["last_result"] = False
        critical_ready = all(r["ready"] for r in results if r["critical"])
        all_ready = all(r["ready"] for r in results)
        return {"ready": critical_ready, "all_ready": all_ready, "checks": results,
                "total": len(results), "passed": sum(1 for r in results if r["ready"])}

    def stats(self) -> dict:
        return {"total_checks": len(self._checks),
                "critical": sum(1 for c in self._checks.values() if c["critical"])}

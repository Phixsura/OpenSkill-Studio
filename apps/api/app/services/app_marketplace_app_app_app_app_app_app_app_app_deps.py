"""App dependency checker — validate app dependencies and compatibility."""
from __future__ import annotations


def check_dependencies(app_deps: list[dict], available: dict[str, str]) -> dict:
    results = []
    missing = []
    for dep in app_deps:
        name = dep["name"]
        required = dep.get("version", "*")
        installed = available.get(name)
        if not installed:
            missing.append(name)
            results.append({"name": name, "required": required, "installed": None, "status": "missing"})
        else:
            compatible = required == "*" or installed >= required
            results.append({"name": name, "required": required, "installed": installed,
                            "status": "ok" if compatible else "incompatible"})
    all_ok = len(missing) == 0 and all(r["status"] == "ok" for r in results)
    return {"dependencies": results, "total": len(results),
            "missing": missing, "missing_count": len(missing),
            "all_satisfied": all_ok}

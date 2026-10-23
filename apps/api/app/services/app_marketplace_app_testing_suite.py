"""App testing suite — run pre-publish validation tests on apps."""


def run_test_suite(*, app_id: str, manifest: dict) -> dict:
    checks = []
    # Manifest checks
    checks.append({"name": "has_name", "passed": bool(manifest.get("name")),
                    "message": "App name is required"})
    checks.append({"name": "has_version", "passed": bool(manifest.get("version")),
                    "message": "Version is required"})
    checks.append({"name": "has_description", "passed": len(manifest.get("description", "")) >= 20,
                    "message": "Description must be at least 20 chars"})
    checks.append({"name": "has_icon", "passed": bool(manifest.get("icon")),
                    "message": "App icon is required"})
    checks.append({"name": "valid_permissions", "passed": isinstance(manifest.get("permissions", []), list),
                    "message": "Permissions must be a list"})
    # Entry point check
    entry = manifest.get("entry_point", "")
    checks.append({"name": "valid_entry", "passed": entry.endswith((".js", ".ts", ".py")),
                    "message": "Entry point must be .js, .ts, or .py"})

    passed = sum(1 for c in checks if c["passed"])
    return {
        "app_id": app_id,
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "all_passed": passed == len(checks),
        "ready_to_publish": passed == len(checks),
        "score": round(passed / len(checks) * 100),
    }

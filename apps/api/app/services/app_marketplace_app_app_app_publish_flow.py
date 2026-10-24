"""App publish flow — complete app publishing pipeline."""

import html
import secrets
from datetime import datetime, timezone

PUBLISH_CHECKS = ["manifest_valid", "tests_passing", "security_scan", "screenshots",
                   "description", "privacy_policy", "version_bumped"]


def start_publish(*, app_id: str, version: str, release_notes: str = "") -> dict:
    publish_id = f"pub_{secrets.token_hex(8)}"
    return {
        "publish_id": publish_id, "app_id": app_id, "version": version,
        "release_notes": html.escape(release_notes),
        "status": "validating", "checks": PUBLISH_CHECKS,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def run_publish_checks(*, results: dict[str, bool]) -> dict:
    checks = []
    passed = 0
    for check in PUBLISH_CHECKS:
        is_pass = results.get(check, False)
        if is_pass:
            passed += 1
        checks.append({"check": check, "label": check.replace("_", " ").title(), "pass": is_pass})
    can_publish = passed == len(PUBLISH_CHECKS)
    return {"checks": checks, "passed": passed, "total": len(PUBLISH_CHECKS),
            "can_publish": can_publish, "score": round(passed / len(PUBLISH_CHECKS) * 100)}


def complete_publish(*, publish_id: str, app_id: str, version: str) -> dict:
    return {"publish_id": publish_id, "app_id": app_id, "version": version,
            "status": "published", "published_at": datetime.now(timezone.utc).isoformat(),
            "message": f"🎉 v{version} is now live on the marketplace!"}

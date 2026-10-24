"""App listing validator — ensure marketplace listings meet quality standards."""
from __future__ import annotations
import html
import re

URL_RE = re.compile(r"^https://\S+$")


def validate_listing(listing: dict) -> dict:
    checks = []
    # Name
    name = listing.get("name", "")
    checks.append({"field": "name", "passed": 3 <= len(name) <= 50,
                    "message": "Name must be 3-50 characters"})
    # Description
    desc = listing.get("description", "")
    checks.append({"field": "description", "passed": len(desc) >= 50,
                    "message": "Description must be at least 50 characters"})
    # Icon
    checks.append({"field": "icon", "passed": bool(listing.get("icon")),
                    "message": "Icon is required"})
    # Category
    checks.append({"field": "category", "passed": bool(listing.get("category")),
                    "message": "Category is required"})
    # Screenshots
    screenshots = listing.get("screenshots", [])
    checks.append({"field": "screenshots", "passed": len(screenshots) >= 1,
                    "message": "At least 1 screenshot required"})
    # Privacy URL
    privacy = listing.get("privacy_url", "")
    checks.append({"field": "privacy_url",
                    "passed": not privacy or bool(URL_RE.match(privacy)),
                    "message": "Privacy URL must be HTTPS"})
    passed = sum(1 for c in checks if c["passed"])
    return {"checks": checks, "passed": passed, "total": len(checks),
            "score": round(passed / len(checks) * 100),
            "ready": all(c["passed"] for c in checks)}

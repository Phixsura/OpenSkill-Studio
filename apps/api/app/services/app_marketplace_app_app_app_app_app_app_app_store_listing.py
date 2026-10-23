"""App store listing builder — build marketplace listings."""
from __future__ import annotations
import html


def build_listing(name: str, tagline: str, description: str, category: str,
                   pricing: str = "free", screenshots: int = 0, features: list[str] | None = None) -> dict:
    completeness = 0
    if name:
        completeness += 20
    if tagline:
        completeness += 15
    if description and len(description) >= 50:
        completeness += 25
    if screenshots >= 3:
        completeness += 20
    if features and len(features) >= 3:
        completeness += 20
    return {"name": html.escape(name), "tagline": html.escape(tagline),
            "description": html.escape(description), "category": category,
            "pricing": pricing, "screenshots": screenshots,
            "features": features or [], "completeness_pct": completeness,
            "ready_to_publish": completeness >= 80}


def validate_listing(listing: dict) -> dict:
    issues = []
    if not listing.get("name"):
        issues.append("Name is required")
    if not listing.get("tagline"):
        issues.append("Tagline is required")
    if len(listing.get("description", "")) < 50:
        issues.append("Description must be at least 50 characters")
    if listing.get("screenshots", 0) < 1:
        issues.append("At least 1 screenshot required")
    return {"valid": len(issues) == 0, "issues": issues, "issue_count": len(issues)}

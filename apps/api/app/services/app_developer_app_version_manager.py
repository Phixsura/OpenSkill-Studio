"""App version manager — high-level version lifecycle operations."""


def compute_version_status(versions: list[dict]) -> dict:
    """Compute version status summary."""
    total = len(versions)
    approved = sum(1 for v in versions if v.get("review_status") == "approved")
    pending = sum(1 for v in versions if v.get("review_status") == "pending")
    rejected = sum(1 for v in versions if v.get("review_status") == "rejected")
    latest = versions[0] if versions else None
    return {
        "total": total, "approved": approved, "pending": pending, "rejected": rejected,
        "latest_version": latest.get("version") if latest else None,
        "latest_status": latest.get("review_status") if latest else None,
        "has_pending": pending > 0,
    }


def can_create_new_version(versions: list[dict]) -> dict:
    """Check if a new version can be created (no pending reviews)."""
    pending = [v for v in versions if v.get("review_status") == "pending"]
    return {"allowed": len(pending) == 0, "pending_count": len(pending),
            "reason": "Cannot create new version while review is pending" if pending else None}

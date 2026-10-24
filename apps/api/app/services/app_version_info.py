"""Version info helper."""

def format_version_info(version: str, review_status: str, created_at: str) -> dict:
    return {"version": version, "review_status": review_status, "created_at": created_at,
            "is_approved": review_status == "approved", "is_latest": False}

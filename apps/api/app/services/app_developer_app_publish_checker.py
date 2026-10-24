"""App publish checker — verify all requirements before publishing."""


def check_publish_requirements(*, app: dict, latest_version: dict | None, developer: dict) -> dict:
    errors = []
    warnings = []
    
    if app.get("status") != "approved":
        errors.append("App must be in 'approved' status")
    if not latest_version or latest_version.get("review_status") != "approved":
        errors.append("Latest version must be approved")
    if not app.get("description"):
        errors.append("App description is required")
    if app.get("visibility") != "public":
        warnings.append("App visibility is not public — only public apps appear in marketplace")
    if not developer.get("verified"):
        warnings.append("Unverified developer — apps may have limited visibility")
    if not app.get("privacy_policy_url"):
        warnings.append("No privacy policy URL — recommended for trust")
    
    return {"can_publish": len(errors) == 0, "errors": errors, "warnings": warnings}

"""Marketplace app validator — validate an app is ready for marketplace listing."""


def validate_marketplace_ready(app: dict, *, version: dict | None = None, developer: dict | None = None) -> dict:
    errors = []
    warnings = []
    
    if app.get("status") != "published":
        errors.append("App must be published")
    if not app.get("description"):
        errors.append("Description is required for marketplace listing")
    if app.get("visibility") != "public":
        errors.append("App must be public")
    
    if version and version.get("review_status") != "approved":
        errors.append("Latest version must be approved")
    
    if developer and not developer.get("verified"):
        warnings.append("Unverified developer — apps may have lower visibility")
    
    if not app.get("icon_url"):
        warnings.append("Adding an icon improves discoverability")
    if not app.get("homepage_url"):
        warnings.append("Adding a homepage URL builds trust")
    
    return {"ready": len(errors) == 0, "errors": errors, "warnings": warnings}

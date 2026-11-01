"""Permissions dialog — explain and request permissions during install."""

PERMISSION_EXPLANATIONS = {
    "read:users": "View basic user information like names and email addresses",
    "write:users": "Create and update user profiles on behalf of the organization",
    "read:projects": "View project details, status, and metadata",
    "write:projects": "Create and modify projects",
    "read:billing": "View billing information and invoices",
    "admin:org": "Full administrative access to organization settings",
    "webhooks:manage": "Create, update, and delete webhook endpoints",
    "secrets:read": "Access stored secrets and API keys",
}

def build_permissions_dialog(*, required: list[str], optional: list[str]) -> dict:
    req = [{"scope": s, "explanation": PERMISSION_EXPLANATIONS.get(s, s), "required": True} for s in required]
    opt = [{"scope": s, "explanation": PERMISSION_EXPLANATIONS.get(s, s), "required": False} for s in optional]
    sensitive = [p for p in req + opt if p["scope"] in ("admin:org", "secrets:read", "read:billing")]
    return {"required_permissions": req, "optional_permissions": opt,
            "total": len(req) + len(opt), "has_sensitive": len(sensitive) > 0,
            "sensitive_permissions": sensitive}

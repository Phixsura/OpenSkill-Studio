"""Tenant isolation — ensure data isolation between organizations using apps."""


def validate_tenant_access(*, org_id: str, resource_org_id: str) -> dict:
    if not org_id:
        return {"allowed": False, "error": "Missing org_id"}
    if org_id != resource_org_id:
        return {"allowed": False, "error": "Cross-tenant access denied"}
    return {"allowed": True, "error": None}


def build_tenant_context(*, org_id: str, user_id: str, app_id: str, installation_id: str) -> dict:
    return {"org_id": org_id, "user_id": user_id, "app_id": app_id,
            "installation_id": installation_id,
            "namespace": f"org_{org_id}_app_{app_id}",
            "data_prefix": f"data/{org_id}/{app_id}/"}


def check_data_boundary(*, requested_path: str, allowed_prefix: str) -> dict:
    if not requested_path.startswith(allowed_prefix):
        return {"allowed": False, "error": f"Path outside tenant boundary: {requested_path}"}
    if ".." in requested_path:
        return {"allowed": False, "error": "Path traversal not allowed"}
    return {"allowed": True, "error": None}

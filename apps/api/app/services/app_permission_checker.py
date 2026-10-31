"""Permission checker — check if an app operation is allowed."""

from app.services.app_scope_constants import ALL_SCOPES


def check_operation(*, granted_scopes: list[str], required_scope: str) -> dict:
    """Check if an operation is allowed by granted scopes."""
    if required_scope not in ALL_SCOPES:
        return {"allowed": False, "reason": f"Unknown scope: {required_scope}"}
    if required_scope in granted_scopes:
        return {"allowed": True}
    return {"allowed": False, "reason": f"Missing scope: {required_scope}"}


def check_bulk_operations(*, granted_scopes: list[str], operations: list[dict]) -> dict:
    """Check multiple operations at once."""
    results = []
    for op in operations:
        result = check_operation(granted_scopes=granted_scopes, required_scope=op.get("scope", ""))
        results.append({**op, **result})
    denied = [r for r in results if not r["allowed"]]
    return {"all_allowed": len(denied) == 0, "total": len(operations), "denied": len(denied), "results": results}

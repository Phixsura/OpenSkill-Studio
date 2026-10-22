"""Token scoping — fine-grained access token management with scope hierarchies."""

SCOPE_HIERARCHY = {
    "admin": {"read", "write", "delete", "manage_team", "manage_billing"},
    "write": {"read"},
    "manage_team": {"read"},
    "manage_billing": {"read"},
    "read": set(),
    "delete": {"read"},
}


def expand_scopes(*, scopes: list[str]) -> set[str]:
    expanded = set()
    for scope in scopes:
        expanded.add(scope)
        expanded.update(SCOPE_HIERARCHY.get(scope, set()))
    # Recursively expand
    prev_size = 0
    while len(expanded) != prev_size:
        prev_size = len(expanded)
        for scope in list(expanded):
            expanded.update(SCOPE_HIERARCHY.get(scope, set()))
    return expanded


def check_scope(*, token_scopes: list[str], required_scope: str) -> bool:
    return required_scope in expand_scopes(scopes=token_scopes)


def create_scoped_token(*, app_id: str, scopes: list[str], name: str) -> dict:
    valid = set(SCOPE_HIERARCHY.keys())
    invalid = set(scopes) - valid
    if invalid:
        return {"error": f"Invalid scopes: {', '.join(sorted(invalid))}"}
    expanded = expand_scopes(scopes=scopes)
    return {"app_id": app_id, "name": name, "granted_scopes": sorted(scopes),
            "effective_scopes": sorted(expanded), "error": None}

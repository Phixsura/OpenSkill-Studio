"""Team role manager — assign and check role-based permissions."""
from __future__ import annotations

ROLES = {
    "owner": {"level": 100, "permissions": ["*"]},
    "admin": {"level": 80, "permissions": ["manage_members", "manage_settings", "deploy", "view"]},
    "developer": {"level": 50, "permissions": ["deploy", "view", "edit_code"]},
    "viewer": {"level": 10, "permissions": ["view"]},
}

_members: dict[str, dict] = {}


def add_member(user_id: str, role: str, added_by: str) -> dict:
    if role not in ROLES:
        return {"added": False, "error": "invalid_role"}
    _members[user_id] = {"user_id": user_id, "role": role, "added_by": added_by}
    return {"added": True, "user_id": user_id, "role": role}


def check_access(user_id: str, permission: str) -> bool:
    member = _members.get(user_id)
    if not member:
        return False
    role_perms = ROLES.get(member["role"], {}).get("permissions", [])
    return "*" in role_perms or permission in role_perms


def change_role(user_id: str, new_role: str, changed_by: str) -> dict:
    if new_role not in ROLES:
        return {"changed": False, "error": "invalid_role"}
    if user_id not in _members:
        return {"changed": False, "error": "not_member"}
    changer = _members.get(changed_by)
    target = _members[user_id]
    if changer and ROLES[changer["role"]]["level"] <= ROLES[target["role"]]["level"]:
        return {"changed": False, "error": "insufficient_permission"}
    _members[user_id]["role"] = new_role
    return {"changed": True, "user_id": user_id, "new_role": new_role}


def list_members() -> list[dict]:
    return list(_members.values())


def clear_members() -> None:
    _members.clear()

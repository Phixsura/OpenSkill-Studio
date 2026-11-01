"""Developer team management — manage team members for a developer account."""

from collections import defaultdict

_teams: dict[str, list[dict]] = defaultdict(list)

VALID_ROLES = {"owner", "admin", "member", "viewer"}


def add_member(developer_id: str, *, user_id: str, role: str = "member") -> dict | None:
    if role not in VALID_ROLES:
        return None
    if any(m["user_id"] == user_id for m in _teams[developer_id]):
        return None  # already a member
    member = {"user_id": user_id, "role": role}
    _teams[developer_id].append(member)
    return member


def remove_member(developer_id: str, user_id: str) -> bool:
    before = len(_teams[developer_id])
    _teams[developer_id] = [m for m in _teams[developer_id] if m["user_id"] != user_id]
    return len(_teams[developer_id]) < before


def list_members(developer_id: str) -> list[dict]:
    return _teams.get(developer_id, [])


def get_role(developer_id: str, user_id: str) -> str | None:
    for m in _teams.get(developer_id, []):
        if m["user_id"] == user_id:
            return m["role"]
    return None


def has_permission(developer_id: str, user_id: str, *, min_role: str = "member") -> bool:
    role = get_role(developer_id, user_id)
    if not role:
        return False
    hierarchy = {"viewer": 0, "member": 1, "admin": 2, "owner": 3}
    return hierarchy.get(role, 0) >= hierarchy.get(min_role, 0)

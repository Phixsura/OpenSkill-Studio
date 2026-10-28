"""App Team Member — manage team members and roles for installed apps.

Manages team membership:
- Add/remove team members
- Assign roles (owner, admin, member, viewer)
- Role hierarchy for access control
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

ROLE_HIERARCHY = {"owner": 3, "admin": 2, "member": 1, "viewer": 0}


@dataclass
class TeamMember:
    """A team member."""

    user_id: str
    email: str
    role: str
    display_name: str = ""


class AppTeamMember:
    """Manage team members and roles."""

    def __init__(self) -> None:
        # (installation_id, user_id) → TeamMember
        self._members: dict[tuple[str, str], TeamMember] = {}

    def add_member(
        self,
        installation_id: str,
        user_id: str,
        email: str,
        role: str = "member",
        display_name: str = "",
    ) -> TeamMember:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")
        if role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {role}")

        key = (installation_id, user_id)
        if key in self._members:
            raise ValueError(f"Member {user_id} already exists")

        member = TeamMember(
            user_id=user_id, email=email,
            role=role, display_name=display_name or email,
        )
        self._members[key] = member
        return member

    def update_role(
        self, installation_id: str, user_id: str, new_role: str
    ) -> TeamMember:
        if new_role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {new_role}")
        member = self._get(installation_id, user_id)
        member.role = new_role
        return member

    def remove_member(self, installation_id: str, user_id: str) -> bool:
        key = (installation_id, user_id)
        if key in self._members:
            del self._members[key]
            return True
        return False

    def has_role_or_higher(
        self, installation_id: str, user_id: str, min_role: str
    ) -> bool:
        """Check if user has the specified role or higher."""
        member = self._members.get((installation_id, user_id))
        if member is None:
            return False
        return ROLE_HIERARCHY.get(member.role, -1) >= ROLE_HIERARCHY.get(min_role, 999)

    def list_members(
        self, installation_id: str, role: str | None = None
    ) -> list[TeamMember]:
        members = [m for (inst, _), m in self._members.items() if inst == installation_id]
        if role:
            members = [m for m in members if m.role == role]
        return members

    def member_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._members if inst == installation_id)

    def _get(self, installation_id: str, user_id: str) -> TeamMember:
        key = (installation_id, user_id)
        m = self._members.get(key)
        if m is None:
            raise KeyError(f"Member {user_id} not found")
        return m

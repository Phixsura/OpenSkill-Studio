"""Consumer Team Member — manage team members within a consumer organization."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class TeamMember:
    member_id: str
    consumer_id: str
    email: str
    role: str = "member"  # "owner", "admin", "member", "viewer"
    joined_at: datetime | None = None
    invited_by: str | None = None

ROLE_HIERARCHY = {"owner": 4, "admin": 3, "member": 2, "viewer": 1}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember:
    def __init__(self) -> None:
        self._members: dict[tuple[str, str, str], TeamMember] = {}  # (inst, consumer, member_id)

    def add_member(self, installation_id: str, member: TeamMember) -> TeamMember:
        if not installation_id:
            raise ValueError("installation_id is required")
        if member.role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {member.role}")
        key = (installation_id, member.consumer_id, member.member_id)
        if key in self._members:
            raise ValueError(f"Member {member.member_id} already exists")
        member.joined_at = member.joined_at or datetime.utcnow()
        self._members[key] = member
        log.info("member_added", installation_id=installation_id, consumer_id=member.consumer_id, member=member.member_id, role=member.role)
        return member

    def update_role(self, installation_id: str, consumer_id: str, member_id: str, new_role: str, by_member_id: str) -> TeamMember:
        if new_role not in ROLE_HIERARCHY:
            raise ValueError(f"Invalid role: {new_role}")
        actor_key = (installation_id, consumer_id, by_member_id)
        actor = self._members.get(actor_key)
        if not actor:
            raise ValueError("Acting member not found")
        if ROLE_HIERARCHY.get(actor.role, 0) < ROLE_HIERARCHY.get(new_role, 0):
            raise ValueError("Cannot assign role higher than your own")
        key = (installation_id, consumer_id, member_id)
        member = self._members.get(key)
        if not member:
            raise ValueError("Member not found")
        member.role = new_role
        return member

    def remove_member(self, installation_id: str, consumer_id: str, member_id: str) -> None:
        key = (installation_id, consumer_id, member_id)
        member = self._members.get(key)
        if not member:
            raise ValueError("Member not found")
        if member.role == "owner":
            owners = [m for (i, c, _), m in self._members.items() if i == installation_id and c == consumer_id and m.role == "owner"]
            if len(owners) <= 1:
                raise ValueError("Cannot remove the last owner")
        del self._members[key]

    def list_members(self, installation_id: str, consumer_id: str) -> list[TeamMember]:
        return sorted([m for (inst, cid, _), m in self._members.items() if inst == installation_id and cid == consumer_id], key=lambda m: -ROLE_HIERARCHY.get(m.role, 0))

    def get_member(self, installation_id: str, consumer_id: str, member_id: str) -> TeamMember | None:
        return self._members.get((installation_id, consumer_id, member_id))

"""Developer Team Manager — manage team members and roles for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class TeamMember:
    user_id: str
    role: str  # owner, admin, developer, viewer
    joined_at: float = 0.0
    invited_by: str = ""
    def __post_init__(self):
        if not self.joined_at: self.joined_at = time.time()


@dataclass
class Team:
    team_id: str
    name: str
    extension_id: str
    members: dict[str, TeamMember] = field(default_factory=dict)

ROLE_HIERARCHY = {"owner": 4, "admin": 3, "developer": 2, "viewer": 1}


class DevTeamMgrService:
    def __init__(self):
        self._teams: dict[str, Team] = {}
        self._counter = 0

    def create(self, name: str, extension_id: str, owner_id: str) -> Team:
        self._counter += 1
        tid = f"team-{self._counter}"
        team = Team(team_id=tid, name=name, extension_id=extension_id)
        team.members[owner_id] = TeamMember(user_id=owner_id, role="owner")
        self._teams[tid] = team
        return team

    def add_member(self, team_id: str, user_id: str, role: str,
                   invited_by: str) -> bool:
        team = self._teams.get(team_id)
        if not team or role not in ROLE_HIERARCHY or role == "owner":
            return False
        if user_id in team.members:
            return False
        inviter = team.members.get(invited_by)
        if not inviter or ROLE_HIERARCHY[inviter.role] <= ROLE_HIERARCHY[role]:
            return False
        team.members[user_id] = TeamMember(user_id=user_id, role=role,
                                           invited_by=invited_by)
        return True

    def remove_member(self, team_id: str, user_id: str, removed_by: str) -> bool:
        team = self._teams.get(team_id)
        if not team: return False
        target = team.members.get(user_id)
        remover = team.members.get(removed_by)
        if not target or not remover: return False
        if target.role == "owner": return False
        if ROLE_HIERARCHY[remover.role] <= ROLE_HIERARCHY[target.role]:
            return False
        del team.members[user_id]
        return True

    def get_members(self, team_id: str) -> list[TeamMember]:
        team = self._teams.get(team_id)
        return list(team.members.values()) if team else []

    def has_permission(self, team_id: str, user_id: str, min_role: str) -> bool:
        team = self._teams.get(team_id)
        if not team: return False
        member = team.members.get(user_id)
        if not member: return False
        return ROLE_HIERARCHY.get(member.role, 0) >= ROLE_HIERARCHY.get(min_role, 0)

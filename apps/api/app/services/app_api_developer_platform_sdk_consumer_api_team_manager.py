"""Consumer Team Manager — team-based API access with roles."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

ROLES = ("owner", "admin", "developer", "viewer")


@dataclass
class TeamMember:
    user_id: str
    role: str
    joined_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Team:
    team_id: str
    name: str
    consumer_id: str
    members: dict[str, TeamMember] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TeamManager:
    """Manage teams with role-based access for API consumers."""

    _teams: dict[str, Team] = field(default_factory=dict)

    def create_team(self, team_id: str, name: str, consumer_id: str,
                    owner_id: str) -> dict:
        if team_id in self._teams:
            raise ValueError(f"Team {team_id} already exists")
        team = Team(team_id=team_id, name=name, consumer_id=consumer_id)
        team.members[owner_id] = TeamMember(user_id=owner_id, role="owner")
        self._teams[team_id] = team
        logger.info("team_created", team_id=team_id, owner=owner_id)
        return {"team_id": team_id, "name": name, "owner": owner_id}

    def add_member(self, team_id: str, user_id: str, role: str = "developer") -> dict:
        team = self._teams.get(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        if role not in ROLES:
            raise ValueError(f"Invalid role: {role}")
        if user_id in team.members:
            raise ValueError(f"User {user_id} already in team")
        team.members[user_id] = TeamMember(user_id=user_id, role=role)
        logger.info("member_added", team_id=team_id, user_id=user_id, role=role)
        return {"team_id": team_id, "user_id": user_id, "role": role,
                "member_count": len(team.members)}

    def remove_member(self, team_id: str, user_id: str) -> dict:
        team = self._teams.get(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        member = team.members.get(user_id)
        if not member:
            return {"removed": False, "reason": "not_a_member"}
        if member.role == "owner":
            owners = sum(1 for m in team.members.values() if m.role == "owner")
            if owners <= 1:
                raise ValueError("Cannot remove last owner")
        del team.members[user_id]
        return {"removed": True, "member_count": len(team.members)}

    def change_role(self, team_id: str, user_id: str, new_role: str) -> dict:
        team = self._teams.get(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        if new_role not in ROLES:
            raise ValueError(f"Invalid role: {new_role}")
        member = team.members.get(user_id)
        if not member:
            raise ValueError(f"User {user_id} not in team")
        old_role = member.role
        member.role = new_role
        return {"user_id": user_id, "old_role": old_role, "new_role": new_role}

    def check_permission(self, team_id: str, user_id: str,
                         required_role: str) -> dict:
        team = self._teams.get(team_id)
        if not team:
            return {"allowed": False, "reason": "team_not_found"}
        member = team.members.get(user_id)
        if not member:
            return {"allowed": False, "reason": "not_a_member"}
        role_hierarchy = {r: i for i, r in enumerate(ROLES)}
        allowed = role_hierarchy.get(member.role, 99) <= role_hierarchy.get(required_role, 99)
        return {"allowed": allowed, "user_role": member.role,
                "required_role": required_role}

    def get_team(self, team_id: str) -> dict | None:
        team = self._teams.get(team_id)
        if not team:
            return None
        return {
            "team_id": team.team_id, "name": team.name,
            "consumer_id": team.consumer_id,
            "member_count": len(team.members),
            "members": [{"user_id": m.user_id, "role": m.role}
                        for m in team.members.values()],
        }

    def list_teams(self, consumer_id: str | None = None) -> list[dict]:
        teams = list(self._teams.values())
        if consumer_id:
            teams = [t for t in teams if t.consumer_id == consumer_id]
        return [{"team_id": t.team_id, "name": t.name,
                 "member_count": len(t.members)} for t in teams]

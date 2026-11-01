"""App API Developer Team Manager — manage developer teams and roles."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

ROLES = {"owner", "admin", "developer", "viewer"}

@dataclass
class TeamMember:
    developer_id: str
    role: str
    joined_at: float = 0.0

@dataclass
class DeveloperTeam:
    team_id: str
    name: str
    members: list[TeamMember] = field(default_factory=list)

    @property
    def member_count(self) -> int:
        return len(self.members)

class AppAPIDeveloperAPIApiDeveloperTeamManager:
    def __init__(self) -> None:
        self._teams: dict[tuple[str, str], DeveloperTeam] = {}

    def create_team(self, installation_id: str, team_id: str, name: str, owner_id: str) -> DeveloperTeam:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, team_id)
        if key in self._teams: raise ValueError(f"Team {team_id} exists")
        t = DeveloperTeam(team_id=team_id, name=name, members=[TeamMember(developer_id=owner_id, role="owner")])
        self._teams[key] = t
        return t

    def add_member(self, installation_id: str, team_id: str, developer_id: str, role: str) -> DeveloperTeam:
        if role not in ROLES: raise ValueError(f"Invalid role: {role}")
        t = self._get(installation_id, team_id)
        if any(m.developer_id == developer_id for m in t.members): raise ValueError("Already a member")
        t.members.append(TeamMember(developer_id=developer_id, role=role))
        return t

    def remove_member(self, installation_id: str, team_id: str, developer_id: str) -> DeveloperTeam:
        t = self._get(installation_id, team_id)
        member = next((m for m in t.members if m.developer_id == developer_id), None)
        if member is None: raise KeyError("Not a member")
        if member.role == "owner": raise ValueError("Cannot remove owner")
        t.members = [m for m in t.members if m.developer_id != developer_id]
        return t

    def list_teams(self, installation_id: str) -> list[DeveloperTeam]:
        return [t for (inst, _), t in self._teams.items() if inst == installation_id]

    def _get(self, installation_id: str, team_id: str) -> DeveloperTeam:
        key = (installation_id, team_id)
        t = self._teams.get(key)
        if t is None: raise KeyError(f"Team {team_id} not found")
        return t

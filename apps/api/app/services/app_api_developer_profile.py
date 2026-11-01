"""App API Developer Profile — manage developer profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeveloperProfile:
    developer_id: str
    display_name: str
    email: str
    bio: str = ""
    avatar_url: str = ""
    app_count: int = 0
    api_key_count: int = 0

class AppAPIDeveloperProfile:
    def __init__(self) -> None:
        self._profiles: dict[tuple[str, str], DeveloperProfile] = {}

    def create(self, installation_id: str, developer_id: str, display_name: str, email: str, bio: str = "") -> DeveloperProfile:
        if not installation_id: raise ValueError("installation_id is required")
        if not email or "@" not in email: raise ValueError("valid email required")
        key = (installation_id, developer_id)
        if key in self._profiles: raise ValueError(f"Profile {developer_id} exists")
        p = DeveloperProfile(developer_id=developer_id, display_name=display_name, email=email, bio=bio)
        self._profiles[key] = p
        return p

    def update(self, installation_id: str, developer_id: str, **kwargs) -> DeveloperProfile:
        p = self._get(installation_id, developer_id)
        for k, v in kwargs.items():
            if hasattr(p, k) and k != "developer_id": setattr(p, k, v)
        return p

    def get(self, installation_id: str, developer_id: str) -> DeveloperProfile:
        return self._get(installation_id, developer_id)

    def search(self, installation_id: str, query: str) -> list[DeveloperProfile]:
        q = query.lower()
        return [p for (inst, _), p in self._profiles.items() if inst == installation_id and (q in p.display_name.lower() or q in p.email.lower())]

    def list_profiles(self, installation_id: str) -> list[DeveloperProfile]:
        return [p for (inst, _), p in self._profiles.items() if inst == installation_id]

    def _get(self, installation_id: str, developer_id: str) -> DeveloperProfile:
        p = self._profiles.get((installation_id, developer_id))
        if p is None: raise KeyError(f"Profile {developer_id} not found")
        return p

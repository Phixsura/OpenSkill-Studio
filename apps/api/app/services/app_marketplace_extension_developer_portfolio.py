"""Developer Portfolio — showcase developer's extensions and achievements.

Public profile with published extensions, badges, certifications,
contribution stats, and social links.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DeveloperPortfolio:
    developer_id: str
    display_name: str = ""
    bio: str = ""
    avatar_url: str = ""
    website: str = ""
    github: str = ""
    extensions: list[str] = field(default_factory=list)
    badges: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    total_installs: int = 0
    avg_rating: float = 0.0
    member_since: str = ""


class DeveloperPortfolioService:
    """Manages public developer portfolios."""

    def __init__(self):
        self._portfolios: dict[str, DeveloperPortfolio] = {}

    def create_or_update(self, developer_id: str, **kwargs) -> DeveloperPortfolio:
        if developer_id not in self._portfolios:
            self._portfolios[developer_id] = DeveloperPortfolio(developer_id=developer_id)
        portfolio = self._portfolios[developer_id]
        for k, v in kwargs.items():
            if hasattr(portfolio, k):
                setattr(portfolio, k, v)
        return portfolio

    def get(self, developer_id: str) -> DeveloperPortfolio | None:
        return self._portfolios.get(developer_id)

    def get_public(self, developer_id: str) -> dict | None:
        p = self._portfolios.get(developer_id)
        if not p:
            return None
        return {
            "name": p.display_name, "bio": p.bio, "avatar": p.avatar_url,
            "website": p.website, "github": p.github,
            "extensions": len(p.extensions), "badges": len(p.badges),
            "certifications": len(p.certifications),
            "total_installs": p.total_installs, "avg_rating": p.avg_rating,
        }

    def search(self, query: str) -> list[DeveloperPortfolio]:
        q = query.lower()
        return [p for p in self._portfolios.values()
                if q in p.display_name.lower() or q in p.bio.lower()]

    def get_top_developers(self, limit: int = 10) -> list[DeveloperPortfolio]:
        return sorted(self._portfolios.values(),
                      key=lambda p: p.total_installs, reverse=True)[:limit]

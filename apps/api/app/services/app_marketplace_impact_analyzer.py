"""Impact Analyzer — assess the impact of extension changes.

Analyzes the blast radius of changes: how many orgs, users, and
dependent extensions are affected by updates, deprecations, or outages.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ImpactAssessment:
    extension_id: str
    change_type: str  # update, deprecate, remove, outage
    affected_orgs: int
    affected_users: int
    dependent_extensions: int
    risk_level: str  # low, medium, high, critical
    recommendations: list[str] = field(default_factory=list)


class ImpactAnalyzer:
    """Analyzes the blast radius of extension changes."""

    def __init__(self):
        self._install_data: dict[str, dict] = {}  # ext -> {orgs, users, dependents}

    def register_extension_data(self, extension_id: str, org_count: int,
                                 user_count: int, dependent_ids: list[str]) -> None:
        self._install_data[extension_id] = {
            "orgs": org_count, "users": user_count, "dependents": dependent_ids,
        }

    def _calc_risk(self, orgs: int, users: int, dependents: int) -> str:
        score = orgs * 10 + users + dependents * 50
        if score >= 5000:
            return "critical"
        elif score >= 1000:
            return "high"
        elif score >= 100:
            return "medium"
        return "low"

    def analyze_update(self, extension_id: str, breaking: bool = False) -> ImpactAssessment:
        data = self._install_data.get(extension_id, {"orgs": 0, "users": 0, "dependents": []})
        orgs = data["orgs"]
        users = data["users"]
        deps = len(data["dependents"])
        risk = self._calc_risk(orgs, users, deps)

        recs = []
        if breaking and deps > 0:
            recs.append(f"Notify {deps} dependent extension(s) before releasing")
        if breaking and orgs > 10:
            recs.append("Use canary deployment for gradual rollout")
        if risk in ("high", "critical"):
            recs.append("Schedule maintenance window and prepare rollback")
        if not breaking:
            recs.append("Non-breaking change — standard release process")

        return ImpactAssessment(extension_id, "update", orgs, users, deps, risk, recs)

    def analyze_deprecation(self, extension_id: str) -> ImpactAssessment:
        data = self._install_data.get(extension_id, {"orgs": 0, "users": 0, "dependents": []})
        orgs = data["orgs"]
        users = data["users"]
        deps = len(data["dependents"])
        risk = self._calc_risk(orgs * 2, users, deps * 2)  # deprecation is higher impact

        recs = ["Announce deprecation with at least 90 days notice"]
        if deps > 0:
            recs.append(f"Provide migration path for {deps} dependent extension(s)")
        if orgs > 0:
            recs.append(f"Notify {orgs} organization(s) with alternatives")
        return ImpactAssessment(extension_id, "deprecate", orgs, users, deps, risk, recs)

    def analyze_outage(self, extension_id: str) -> ImpactAssessment:
        data = self._install_data.get(extension_id, {"orgs": 0, "users": 0, "dependents": []})
        orgs = data["orgs"]
        users = data["users"]
        deps = len(data["dependents"])
        risk = self._calc_risk(orgs * 3, users * 2, deps * 3)  # outage is highest impact

        recs = ["Initiate incident response immediately"]
        if deps > 0:
            recs.append(f"Alert {deps} dependent extension(s) — cascading failure risk")
        recs.append("Post status page update")
        return ImpactAssessment(extension_id, "outage", orgs, users, deps, risk, recs)

    def compare_impact(self, ext_a: str, ext_b: str) -> dict:
        a = self.analyze_update(ext_a)
        b = self.analyze_update(ext_b)
        return {
            "higher_impact": ext_a if a.affected_orgs + a.affected_users > b.affected_orgs + b.affected_users else ext_b,
            "a": {"id": ext_a, "orgs": a.affected_orgs, "users": a.affected_users, "risk": a.risk_level},
            "b": {"id": ext_b, "orgs": b.affected_orgs, "users": b.affected_users, "risk": b.risk_level},
        }

"""Succession planning — identify and prepare successors for key roles.

Features:
  - Key role designation within org
  - Readiness assessment (ready now, 1-2 years, 3+ years)
  - Successor candidate identification from capability match
  - Development plan generation for succession candidates
  - Risk assessment (roles with no ready successors)
  - Succession pipeline visualization data
"""

from __future__ import annotations

from dataclasses import dataclass

READINESS_LEVELS = {
    "ready_now": {"label": "Ready Now", "score": 1.0},
    "ready_1_year": {"label": "Ready in 1 Year", "score": 0.7},
    "ready_2_years": {"label": "Ready in 2 Years", "score": 0.4},
    "ready_3_plus": {"label": "3+ Years", "score": 0.2},
    "not_ready": {"label": "Not Ready", "score": 0.0},
}

RISK_LEVELS = frozenset({"critical", "high", "medium", "low"})


@dataclass(frozen=True, slots=True)
class KeyRole:
    role_id: str
    org_id: str
    title: str
    required_capabilities: list[dict]  # [{capability_id, min_level}]
    current_holder_id: str | None
    criticality: str  # critical, high, medium
    succession_status: str  # covered, at_risk, critical_gap


@dataclass(frozen=True, slots=True)
class SuccessorCandidate:
    user_id: str
    readiness: str
    readiness_score: float
    capability_match: float  # 0-1
    gaps: list[dict]  # [{capability_name, current_level, required_level}]
    development_actions: list[str]
    time_to_ready_months: int | None


@dataclass(frozen=True, slots=True)
class SuccessionRisk:
    role_id: str
    role_title: str
    criticality: str
    ready_now_count: int
    pipeline_count: int  # total candidates at any readiness
    risk_level: str
    recommendation: str


class SuccessionPlanningService:
    def assess_readiness(
        self,
        *,
        capability_match: float,
        years_experience: float,
        has_leadership_evidence: bool,
    ) -> str:
        """Assess succession readiness level."""
        if capability_match >= 0.9 and years_experience >= 3 and has_leadership_evidence:
            return "ready_now"
        if capability_match >= 0.75 and years_experience >= 2:
            return "ready_1_year"
        if capability_match >= 0.5:
            return "ready_2_years"
        if capability_match >= 0.3:
            return "ready_3_plus"
        return "not_ready"

    def compute_capability_match(
        self,
        user_levels: dict[str, int],
        required: list[dict],
    ) -> float:
        """Compute capability match for a role."""
        if not required:
            return 1.0
        matches = 0
        for req in required:
            cap_id = req.get("capability_id", "")
            min_level = req.get("min_level", 1)
            user_level = user_levels.get(cap_id, 0)
            if user_level >= min_level:
                matches += 1
        return matches / max(len(required), 1)

    def identify_gaps(
        self,
        user_levels: dict[str, int],
        required: list[dict],
    ) -> list[dict]:
        """Identify capability gaps for succession."""
        gaps = []
        for req in required:
            cap_id = req.get("capability_id", "")
            cap_name = req.get("capability_name", cap_id)
            min_level = req.get("min_level", 1)
            current = user_levels.get(cap_id, 0)
            if current < min_level:
                gaps.append(
                    {
                        "capability_name": cap_name,
                        "current_level": current,
                        "required_level": min_level,
                        "gap": min_level - current,
                    }
                )
        return gaps

    def generate_development_actions(
        self,
        gaps: list[dict],
    ) -> list[str]:
        """Generate development action items from gaps."""
        actions = []
        for g in gaps:
            gap_size = g["gap"]
            name = g["capability_name"]
            if gap_size == 1:
                actions.append(f"Gain additional experience in {name} (mentor/project assignment)")
            elif gap_size == 2:
                actions.append(f"Complete structured training program for {name}")
            else:
                actions.append(
                    f"Develop foundational skills in {name} through courses and mentoring"
                )
        return actions

    def assess_risk(
        self,
        *,
        role_id: str,
        role_title: str,
        criticality: str,
        candidates: list[SuccessorCandidate],
    ) -> SuccessionRisk:
        """Assess succession risk for a role."""
        ready_now = sum(1 for c in candidates if c.readiness == "ready_now")
        pipeline = len(candidates)

        if criticality == "critical" and ready_now == 0:
            risk = "critical"
            rec = "URGENT: No succession candidates ready. Start external recruitment and accelerated development."
        elif ready_now == 0 and pipeline > 0:
            risk = "high"
            rec = "Accelerate development of pipeline candidates. Consider interim coverage plan."
        elif ready_now == 1:
            risk = "medium"
            rec = "Single successor identified. Develop additional candidates for redundancy."
        else:
            risk = "low"
            rec = "Succession pipeline is healthy. Maintain development programs."

        return SuccessionRisk(
            role_id=role_id,
            role_title=role_title,
            criticality=criticality,
            ready_now_count=ready_now,
            pipeline_count=pipeline,
            risk_level=risk,
            recommendation=rec,
        )

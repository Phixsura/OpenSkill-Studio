"""Talent ↔ opportunity matching — extends ADR-012 engine (ADR-015 D7).

Wraps the matching engine with talent-specific logic:
  - S1 eligibility: consent-gated (discoverable=true, passport not private)
  - S2 hard constraints: required capabilities at min_level
  - S3 scoring: 5 signals (capability gap, evidence confidence/recency,
    portfolio relevance, credential match)

Two directions:
  - match_candidates_for_opportunity: employer finds candidates
  - match_opportunities_for_user: candidate discovers opportunities
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import structlog
from sqlalchemy import cast, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.talent.models.application import Placement
from app.talent.models.assessment import Credential
from app.talent.models.capability import CapabilityEdge
from app.talent.models.employer import Opportunity
from app.talent.models.evidence import (
    CapabilityEvidence,
)
from app.talent.models.passport import SkillPassport
from app.talent.services.scoring import (
    compute_capability_profile,
)

# Edge types that indicate skill adjacency for partial-credit matching
_ADJACENCY_EDGE_TYPES = frozenset(
    {"related_to", "commonly_paired_with", "specializes", "subsumes"}
)

# Credit multiplier by graph distance (edges traversed)
_ADJACENCY_CREDIT = {1: 0.5, 2: 0.25}

log = structlog.get_logger()

ENGINE_VERSION = "1.0.0"

# Talent matching signal weights (ADR-015 D7)
TALENT_WEIGHTS = {
    "capability_gap_score": 0.40,
    "evidence_confidence": 0.20,
    "evidence_recency": 0.15,
    "portfolio_relevance": 0.15,
    "credential_match": 0.10,
}

_SIGNAL_LABELS = {
    "capability_gap_score": "Meets capability requirements",
    "evidence_confidence": "High-confidence verified evidence",
    "evidence_recency": "Recently demonstrated capabilities",
    "portfolio_relevance": "Relevant project portfolio",
    "credential_match": "Holds relevant credentials",
}


@dataclass
class TalentMatchResult:
    """A single candidate or opportunity match result."""

    entity_id: str
    entity_type: str  # "user" or "opportunity"
    display_name: str
    score: float
    tier: str  # great | good | fair
    reasons: list[dict]
    gaps: list[dict]
    hard_failures: list[dict]
    signals: dict[str, float]


class TalentMatchingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Employer → candidate matching
    # ------------------------------------------------------------------

    async def match_candidates_for_opportunity(
        self,
        opportunity_id: str,
        employer_org_id: str,
        *,
        limit: int = 20,
        explain: bool = False,
    ) -> list[TalentMatchResult]:
        """Find and rank candidates for an opportunity.

        S1: consent gate — only discoverable users with visible passports.
        S2: required capabilities at min_level.
        S3: weighted scoring across 5 signals.

        Only user.id and user.display_name enter the feature space — no
        protected/sensitive attributes are ever queried.
        """
        opp = await self.db.get(Opportunity, opportunity_id)
        if not opp:
            raise ValueError("Opportunity not found")
        if opp.employer_org_id != employer_org_id:
            raise ValueError("Opportunity does not belong to this employer")

        now = datetime.now(UTC)
        required_caps = opp.required_capabilities or []
        preferred_caps = opp.preferred_capabilities or []

        # --- S1: eligibility (consent gate) ---
        # ONLY id + display_name — protected attributes structurally absent
        eligible_q = (
            select(User.id, User.display_name)
            .join(SkillPassport, SkillPassport.user_id == User.id)
            .where(
                SkillPassport.discoverable.is_(True),
                SkillPassport.default_visibility != "private",
                User.status == UserStatus.ACTIVE,
                or_(
                    SkillPassport.discoverable_to.is_(None),
                    SkillPassport.discoverable_to.op("@>")(
                        cast([employer_org_id], JSONB)
                    ),
                ),
            )
        )
        eligible_result = await self.db.execute(eligible_q)
        eligible = [
            {"id": row.id, "display_name": row.display_name}
            for row in eligible_result.all()
        ]

        if not eligible:
            return []

        user_ids = [u["id"] for u in eligible]
        user_names = {u["id"]: u["display_name"] for u in eligible}

        # Pre-load all capability profiles for eligible users
        profiles = await self._bulk_capability_profiles(user_ids, now)

        # Pre-load adjacency graph for all required+preferred capabilities
        all_cap_ids = {
            r.get("capability_id", "")
            for r in required_caps + preferred_caps
            if r.get("capability_id")
        }
        adjacency = await self._load_adjacency_graph(all_cap_ids)

        results: list[TalentMatchResult] = []
        for uid in user_ids:
            profile = profiles.get(uid, {})

            # --- S2: hard constraints (with adjacent skill relaxation) ---
            hard_failures = self._check_hard_constraints(
                profile, required_caps, adjacency=adjacency
            )
            if hard_failures:
                results.append(
                    TalentMatchResult(
                        entity_id=uid,
                        entity_type="user",
                        display_name=user_names[uid],
                        score=0.0,
                        tier="excluded",
                        reasons=[],
                        gaps=[],
                        hard_failures=hard_failures,
                        signals={},
                    )
                )
                continue

            # --- S3: scoring (with partial credit for adjacent skills) ---
            signals = await self._score_candidate(
                uid, profile, required_caps, preferred_caps, now,
                adjacency=adjacency,
            )
            score = sum(
                signals.get(k, 0.0) * w for k, w in TALENT_WEIGHTS.items()
            )
            score = round(score, 4)

            # Reasons and gaps from signal values
            reasons, gaps = self._explain_signals(
                signals, required_caps, preferred_caps, profile,
                adjacency=adjacency,
            )

            tier = (
                "great" if score >= 0.75
                else ("good" if score >= 0.50 else "fair")
            )

            results.append(
                TalentMatchResult(
                    entity_id=uid,
                    entity_type="user",
                    display_name=user_names[uid],
                    score=score,
                    tier=tier,
                    reasons=reasons,
                    gaps=gaps,
                    hard_failures=[],
                    signals=signals,
                )
            )

        # Sort: score desc, tie-break on entity_id asc
        results.sort(key=lambda r: (-r.score, r.entity_id))
        # Separate ranked from excluded
        ranked = [r for r in results if r.tier != "excluded"]
        excluded = [r for r in results if r.tier == "excluded"]

        log.info(
            "talent_match_completed",
            opportunity_id=opportunity_id,
            eligible=len(eligible),
            ranked=len(ranked),
            excluded=len(excluded),
        )

        return ranked[:limit] + excluded

    # ------------------------------------------------------------------
    # Candidate → opportunity matching (reverse)
    # ------------------------------------------------------------------

    async def match_opportunities_for_user(
        self,
        user_id: str,
        *,
        limit: int = 20,
    ) -> list[TalentMatchResult]:
        """Find and rank open opportunities the user qualifies for.

        S1: opportunity.status = 'open'
        S2: user meets all required capabilities at min_level
        S3: same signals, inverted perspective
        """
        now = datetime.now(UTC)

        # Load user profile
        profile_scores = await compute_capability_profile(self.db, user_id)
        profile = {s.capability_id: s for s in profile_scores}

        # S1: open opportunities (capped to avoid loading unbounded sets)
        opp_result = await self.db.execute(
            select(Opportunity)
            .where(Opportunity.status == "open")
            .order_by(Opportunity.created_at.desc())
            .limit(limit * 5)  # Load 5× limit to allow room for filtering
        )
        opportunities = list(opp_result.scalars().all())

        if not opportunities:
            return []

        # Build profile dict for constraint checking
        profile_dict = {
            cap_id: {"level": s.level, "score": s.score, "confidence": s.confidence}
            for cap_id, s in profile.items()
        }

        # Collect all capability IDs across all opportunities for adjacency loading
        all_opp_cap_ids: set[str] = set()
        for opp in opportunities:
            for r in (opp.required_capabilities or []) + (opp.preferred_capabilities or []):
                cid = r.get("capability_id")
                if cid:
                    all_opp_cap_ids.add(cid)
        adjacency = await self._load_adjacency_graph(all_opp_cap_ids)

        results: list[TalentMatchResult] = []
        for opp in opportunities:
            required_caps = opp.required_capabilities or []
            preferred_caps = opp.preferred_capabilities or []

            # S2: hard constraints (with adjacent skill relaxation)
            hard_failures = self._check_hard_constraints(
                profile_dict, required_caps, adjacency=adjacency
            )
            if hard_failures:
                continue  # Don't show opportunities the user can't qualify for

            # S3: score (with partial credit for adjacent skills)
            signals = await self._score_candidate(
                user_id,
                profile_dict,
                required_caps,
                preferred_caps,
                now,
                adjacency=adjacency,
            )
            score = sum(
                signals.get(k, 0.0) * w for k, w in TALENT_WEIGHTS.items()
            )
            score = round(score, 4)

            reasons, gaps = self._explain_signals(
                signals, required_caps, preferred_caps, profile_dict,
                adjacency=adjacency,
            )

            tier = (
                "great" if score >= 0.75
                else ("good" if score >= 0.50 else "fair")
            )

            results.append(
                TalentMatchResult(
                    entity_id=opp.id,
                    entity_type="opportunity",
                    display_name=opp.title,
                    score=score,
                    tier=tier,
                    reasons=reasons,
                    gaps=gaps,
                    hard_failures=[],
                    signals=signals,
                )
            )

        results.sort(key=lambda r: (-r.score, r.entity_id))
        return results[:limit]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _bulk_capability_profiles(
        self,
        user_ids: list[str],
        now: datetime,
    ) -> dict[str, dict]:
        """Load capability profiles for multiple users.

        Returns {user_id: {capability_id: {"level": int, "score": float, "confidence": float}}}
        """
        q = select(CapabilityEvidence).where(
            CapabilityEvidence.user_id.in_(user_ids),
            CapabilityEvidence.status == "active",
        )
        result = await self.db.execute(q)
        all_evidence = result.scalars().all()

        # Group by (user_id, capability_id)
        from collections import defaultdict

        by_user_cap: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for ev in all_evidence:
            by_user_cap[ev.user_id][ev.capability_id].append({
                "score_normalized": float(ev.score_normalized) if ev.score_normalized is not None else None,
                "verification_level": ev.verification_level,
                "confidence": float(ev.confidence),
                "occurred_at": ev.occurred_at,
                "status": ev.status,
                "expires_at": ev.expires_at,
            })

        # Compute scores per user
        from app.talent.models.capability import Capability
        from app.talent.services.scoring import (
            compute_score_from_evidence,
            determine_level,
        )

        # Load all referenced capabilities
        all_cap_ids = set()
        for user_caps in by_user_cap.values():
            all_cap_ids.update(user_caps.keys())

        caps_map: dict[str, Capability] = {}
        if all_cap_ids:
            cap_q = select(Capability).where(Capability.id.in_(all_cap_ids))
            cap_result = await self.db.execute(cap_q)
            caps_map = {c.id: c for c in cap_result.scalars().all()}

        profiles: dict[str, dict] = {}
        for uid, cap_evidence in by_user_cap.items():
            user_profile: dict[str, dict] = {}
            for cap_id, ev_list in cap_evidence.items():
                cap = caps_map.get(cap_id)
                if not cap or cap.status not in ("active", "deprecated"):
                    continue
                score, confidence, substantial = compute_score_from_evidence(
                    ev_list, cap.decay_config, now
                )
                level, _ = determine_level(score, substantial, cap.level_definitions)
                user_profile[cap_id] = {
                    "level": level,
                    "score": score,
                    "confidence": confidence,
                }
            profiles[uid] = user_profile

        return profiles

    async def _load_adjacency_graph(
        self,
        cap_ids: set[str],
    ) -> dict[str, list[tuple[str, int]]]:
        """Load adjacent capabilities up to 2 hops from the given cap IDs.

        Returns {cap_id: [(adjacent_cap_id, distance), ...]} where distance
        is 1 (directly connected) or 2 (connected through an intermediate).
        Both directions of each edge are considered (graph is undirected for
        adjacency purposes).
        """
        if not cap_ids:
            return {}

        # Load all adjacency edges in one batch query
        edge_q = select(CapabilityEdge).where(
            CapabilityEdge.edge_type.in_(_ADJACENCY_EDGE_TYPES),
            or_(
                CapabilityEdge.source_id.in_(cap_ids),
                CapabilityEdge.target_id.in_(cap_ids),
            ),
        )
        result = await self.db.execute(edge_q)
        edges = result.scalars().all()

        # Build undirected adjacency list
        from collections import defaultdict

        adj: dict[str, set[str]] = defaultdict(set)
        for e in edges:
            adj[e.source_id].add(e.target_id)
            adj[e.target_id].add(e.source_id)

        # For each target cap, find adjacent caps at distance 1 and 2
        adjacency: dict[str, list[tuple[str, int]]] = {}
        for cid in cap_ids:
            neighbors: list[tuple[str, int]] = []
            # Distance 1
            for n1 in adj.get(cid, set()):
                neighbors.append((n1, 1))
                # Distance 2 (via n1)
                for n2 in adj.get(n1, set()):
                    if n2 != cid and n2 not in adj.get(cid, set()):
                        neighbors.append((n2, 2))
            adjacency[cid] = neighbors

        return adjacency

    def _check_hard_constraints(
        self,
        profile: dict[str, dict],
        required_caps: list[dict],
        adjacency: dict[str, list[tuple[str, int]]] | None = None,
    ) -> list[dict]:
        """S2: check user meets required capabilities at min_level.

        With adjacency graph: if user lacks cap X but has related cap Y
        (via CapabilityEdge), the constraint is relaxed — treated as a
        partial match (no hard failure), but a gap is noted.
        """
        failures = []
        for req in required_caps:
            cap_id = req.get("capability_id", "")
            min_level = req.get("min_level", 0)
            user_cap = profile.get(cap_id)

            if user_cap and user_cap["level"] >= min_level:
                continue  # Fully met

            # Check adjacent skills if adjacency graph is provided
            if adjacency and cap_id in adjacency:
                has_adjacent = False
                for adj_cap_id, _distance in adjacency[cap_id]:
                    adj_cap = profile.get(adj_cap_id)
                    if adj_cap and adj_cap["level"] >= min_level:
                        has_adjacent = True
                        break
                if has_adjacent:
                    # Adjacent skill meets the level — don't hard-fail,
                    # but it will get partial credit in scoring
                    continue

            # No direct or adjacent match → hard failure
            actual = user_cap["level"] if user_cap else 0
            failures.append({
                "code": "CAPABILITY_BELOW_REQUIRED",
                "capability_id": cap_id,
                "required_level": min_level,
                "actual_level": actual,
                "message": (
                    f"No evidence for required capability (need L{min_level})"
                    if not user_cap
                    else f"Capability L{actual} below required L{min_level}"
                ),
            })
        return failures

    async def _score_candidate(
        self,
        user_id: str,
        profile: dict[str, dict],
        required_caps: list[dict],
        preferred_caps: list[dict],
        now: datetime,
        adjacency: dict[str, list[tuple[str, int]]] | None = None,
    ) -> dict[str, float]:
        """S3: compute all 5 scoring signals for a candidate.

        With adjacency graph: adjacent skills earn partial credit
        (0.5× for distance 1, 0.25× for distance 2).
        """
        import math

        all_caps = required_caps + preferred_caps
        if not all_caps:
            return {k: 0.5 for k in TALENT_WEIGHTS}

        # 1. capability_gap_score: fraction of required + preferred caps met at level
        #    with partial credit for adjacent skills
        met_credit = 0.0
        total_count = len(all_caps)
        for cap_req in all_caps:
            cap_id = cap_req.get("capability_id", "")
            min_level = cap_req.get("min_level", 0)
            user_cap = profile.get(cap_id)
            if user_cap and user_cap["level"] >= min_level:
                met_credit += 1.0  # Full credit
            elif adjacency and cap_id in adjacency:
                # Check adjacent skills for partial credit
                best_credit = 0.0
                for adj_cap_id, distance in adjacency[cap_id]:
                    adj_cap = profile.get(adj_cap_id)
                    if adj_cap and adj_cap["level"] >= min_level:
                        credit = _ADJACENCY_CREDIT.get(distance, 0.0)
                        best_credit = max(best_credit, credit)
                met_credit += best_credit
        capability_gap_score = met_credit / total_count if total_count > 0 else 0.5

        # 2. evidence_confidence: avg confidence across required capabilities
        req_cap_ids = {r.get("capability_id", "") for r in required_caps}
        confidences = [
            profile[cid]["confidence"]
            for cid in req_cap_ids
            if cid in profile
        ]
        evidence_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.0
        )

        # 3. evidence_recency: freshness of most recent evidence per required cap
        # Batch query — one round trip instead of N per-capability queries
        recency_scores = []
        if req_cap_ids:
            batch_q = (
                select(
                    CapabilityEvidence.capability_id,
                    func.max(CapabilityEvidence.occurred_at).label("latest"),
                )
                .where(
                    CapabilityEvidence.user_id == user_id,
                    CapabilityEvidence.capability_id.in_(req_cap_ids),
                    CapabilityEvidence.status == "active",
                )
                .group_by(CapabilityEvidence.capability_id)
            )
            batch_result = await self.db.execute(batch_q)
            for row in batch_result.all():
                age_days = (now - row.latest).total_seconds() / 86400
                recency = math.exp(-0.5 * (age_days / 180) ** 2)
                recency_scores.append(recency)
        evidence_recency = (
            sum(recency_scores) / len(recency_scores) if recency_scores else 0.0
        )

        # 4. portfolio_relevance: count of approved placements / max expected
        placement_q = select(func.count()).where(
            Placement.user_id == user_id,
            Placement.status.in_(["active", "completed"]),
        )
        placement_count = (await self.db.execute(placement_q)).scalar() or 0
        # log1p normalization capped at 1 (same pattern as ADR-012 popularity)
        portfolio_relevance = min(math.log1p(placement_count) / math.log1p(5), 1.0)

        # 5. credential_match: fraction of required caps covered by active credentials
        all_cap_ids = {r.get("capability_id", "") for r in all_caps}
        cred_q = select(Credential).where(
            Credential.user_id == user_id,
            Credential.status == "active",
        )
        cred_result = await self.db.execute(cred_q)
        creds = cred_result.scalars().all()
        cred_cap_ids: set[str] = set()
        for cred in creds:
            for cap_entry in (cred.capabilities or []):
                cid = cap_entry.get("capability_id", "")
                if cid:
                    cred_cap_ids.add(cid)
        cred_overlap = len(all_cap_ids & cred_cap_ids)
        credential_match = cred_overlap / len(all_cap_ids) if all_cap_ids else 0.0

        return {
            "capability_gap_score": round(capability_gap_score, 4),
            "evidence_confidence": round(evidence_confidence, 4),
            "evidence_recency": round(evidence_recency, 4),
            "portfolio_relevance": round(portfolio_relevance, 4),
            "credential_match": round(credential_match, 4),
        }

    def _explain_signals(
        self,
        signals: dict[str, float],
        required_caps: list[dict],
        preferred_caps: list[dict],
        profile: dict[str, dict],
        adjacency: dict[str, list[tuple[str, int]]] | None = None,
    ) -> tuple[list[dict], list[dict]]:
        """Generate reason chips and gap entries from signal values.

        Mirrors the ADR-012 pattern: reasons for values ≥ 0.7, gaps for
        values < 0.4 with weight ≥ 0.10. Also generates ADJACENT_SKILL
        reasons when a related skill earned partial credit.
        """
        reasons: list[dict] = []
        gaps: list[dict] = []

        reason_min = 0.7
        gap_max = 0.4

        for signal_name, value in signals.items():
            weight = TALENT_WEIGHTS.get(signal_name, 0.0)
            label = _SIGNAL_LABELS.get(signal_name, signal_name)

            if value >= reason_min:
                reasons.append({
                    "code": signal_name.upper(),
                    "label": label,
                    "evidence": "verified",
                })
            elif value < gap_max and weight >= 0.10:
                gaps.append({
                    "code": signal_name.upper(),
                    "label": label,
                })

        # Adjacent skill reasons: when a related skill gave partial credit
        all_caps = required_caps + preferred_caps
        if adjacency:
            for cap_req in all_caps:
                cap_id = cap_req.get("capability_id", "")
                min_level = cap_req.get("min_level", 0)
                user_cap = profile.get(cap_id)
                if user_cap and user_cap.get("level", 0) >= min_level:
                    continue  # Directly met — no adjacent reason needed
                if cap_id in adjacency:
                    for adj_cap_id, distance in adjacency[cap_id]:
                        adj_cap = profile.get(adj_cap_id)
                        if adj_cap and adj_cap.get("level", 0) >= min_level:
                            reasons.append({
                                "code": "ADJACENT_SKILL",
                                "capability_id": cap_id,
                                "adjacent_capability_id": adj_cap_id,
                                "distance": distance,
                                "label": f"Related skill at L{adj_cap['level']} (distance {distance})",
                            })
                            break  # Only report the best adjacent match

        # Capability-specific gaps: preferred caps not met
        for pref in preferred_caps:
            cap_id = pref.get("capability_id", "")
            min_level = pref.get("min_level", 0)
            user_cap = profile.get(cap_id)
            if not user_cap or user_cap.get("level", 0) < min_level:
                actual = user_cap.get("level", 0) if user_cap else 0
                gaps.append({
                    "code": "PREFERRED_CAPABILITY_BELOW",
                    "capability_id": cap_id,
                    "label": f"L{actual} (preferred L{min_level})",
                })

        return reasons, gaps

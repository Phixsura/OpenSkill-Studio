"""S3 — deterministic linear scoring over [0,1]-normalized signals.

Reasons and gaps are generated from the SAME signal values used in the sum
(R5: one code path — explanations can never drift from scores).
"""

import math
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_brief import ApplicationStatus, BriefApplication, ClientBrief
from app.models.composer import CreatorCapabilityEvidence
from app.models.project import ReviewStatus, Submission, SubmissionReview

_DIFFICULTY_ORDINAL = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}

_SIGNAL_LABELS = {
    "capability_match": "Provides the requested capabilities",
    "capability_teach_match": "Teaches the required capabilities",
    "scenario_match": "Matches the scenario",
    "output_type_match": "Produces the requested output type",
    "tool_match": "Compatible with the tool constraints",
    "install_popularity": "Widely installed",
    "popularity": "Widely installed",
    "freshness": "Recently published",
    "difficulty_fit": "Fits the learner's level",
    "time_fit": "Fits the time budget",
    "capability_evidence": "Verified capability evidence",
    "recency": "Recently active",
    "rubric_avg": "Strong rubric scores",
    "commercial_history": "Commercial project history",
}

# Evidence provenance per signal for reason chips (D5)
_SIGNAL_EVIDENCE = {
    "capability_evidence": "verified",
    "rubric_avg": "verified",
    "commercial_history": "verified",
    "recency": "verified",
    "capability_match": "declared",
    "capability_teach_match": "declared",
    "scenario_match": "declared",
    "output_type_match": "declared",
    "tool_match": "declared",
    "install_popularity": "verified",
    "popularity": "verified",
    "freshness": "verified",
    "difficulty_fit": "declared",
    "time_fit": "declared",
}


def _now() -> datetime:
    return datetime.now(UTC)


def _fraction_present(requested: list[str], present: set[str], default: float = 1.0) -> float:
    if not requested:
        return default
    return sum(1 for r in requested if r in present) / len(requested)


def _log_popularity(count: int, ceiling: int = 100) -> float:
    return min(math.log1p(max(count, 0)) / math.log1p(ceiling), 1.0)


def _gauss_freshness(created_at: datetime | None, scale_days: float = 30.0) -> float:
    if created_at is None:
        return 0.0
    ref = created_at if created_at.tzinfo else created_at.replace(tzinfo=UTC)
    days = max((_now() - ref).total_seconds() / 86400.0, 0.0)
    return math.exp(-((days / scale_days) ** 2))


def _difficulty_fit(user_level: str | None, entity_level: str | None) -> float:
    if not user_level or not entity_level:
        return 0.5
    u = _DIFFICULTY_ORDINAL.get(user_level)
    e = _DIFFICULTY_ORDINAL.get(entity_level)
    if u is None or e is None:
        return 0.5
    delta = e - u
    if delta == 0:
        return 1.0
    if delta == -1:
        return 0.7
    if delta == 1:
        return 0.5
    return 0.3


async def score(db: AsyncSession, survivors: list, spec, config) -> list[dict]:
    """Score survivors. Returns [{entity, entity_id, score, signals, reasons, gaps}]."""
    requirement = spec.requirement or {}
    weights: dict[str, float] = config.weights or {}
    thresholds: dict = config.thresholds or {}
    reason_min = float(thresholds.get("reason_min", 0.7))
    gap_max = float(thresholds.get("gap_max", 0.4))

    if spec.target_entity_type == "creator":
        signal_rows = await _creator_signals(db, survivors, spec, requirement)
    else:
        signal_rows = [
            (entity, _entity_signals(entity, spec, requirement)) for entity in survivors
        ]

    # A DEFAULTED capability signal is not evidence: when the profile requests
    # no capabilities, _fraction_present returns its 1.0 default and the chip
    # would assert a match that was never tested. Scoring math is unchanged —
    # only the reason row is suppressed. Mirrors the requested-cap folding in
    # _entity_signals per target type.
    if spec.target_entity_type == "skill_pack":
        requested_caps = (
            (requirement.get("required_capabilities") or [])
            # Extracted (soft) caps arrive MERGED into preferred_capabilities
            # (build_match_requirement demotes them there) — no _soft_* key
            # for capabilities exists
            + (requirement.get("preferred_capabilities") or [])
        )
    else:
        requested_caps = (requirement.get("required_capabilities") or []) + (
            requirement.get("preferred_capabilities") or []
        )
    vacuous_signals = (
        set() if requested_caps else {"capability_match", "capability_teach_match"}
    )

    scored: list[dict] = []
    for entity, signals in signal_rows:
        total = sum(weights.get(name, 0.0) * value for name, value in signals.items())
        reasons: list[dict] = []
        gaps: list[dict] = []
        # SAME signal values drive both reasons and gaps (R5)
        for name, value in signals.items():
            weight = weights.get(name, 0.0)
            if value >= reason_min and weight > 0 and name not in vacuous_signals:
                reasons.append(
                    {
                        "code": name.upper(),
                        "label": _SIGNAL_LABELS.get(name, name),
                        "evidence": _SIGNAL_EVIDENCE.get(name, "inferred"),
                    }
                )
            elif value < gap_max and weight >= 0.10:
                gaps.append(
                    {
                        "code": f"LOW_{name.upper()}",
                        "label": f"Weak: {_SIGNAL_LABELS.get(name, name).lower()}",
                    }
                )
        entity_id = entity["id"] if isinstance(entity, dict) else entity.id
        scored.append(
            {
                "entity": entity,
                "entity_id": entity_id,
                "score": round(total, 4),
                "signals": signals,
                "reasons": reasons,
                "gaps": gaps,
            }
        )
    return scored


def _entity_signals(entity, spec, requirement: dict) -> dict[str, float]:
    if spec.target_entity_type == "workflow_pack":
        requested_caps = (requirement.get("required_capabilities") or []) + (
            requirement.get("preferred_capabilities") or []
        )
        caps = set(entity.capability_tags or [])
        scenario = requirement.get("scenario")
        # Scoring may use extracted (soft) values — only hard filters can't (R14)
        output_type = requirement.get("output_type") or requirement.get("_soft_output_type")
        tools = requirement.get("tool_constraints") or []
        out_types = {o.get("type") for o in (entity.output_schema or [])}
        return {
            "capability_match": _fraction_present(requested_caps, caps),
            "scenario_match": (
                0.5 if not scenario else (1.0 if scenario in (entity.scenario_tags or []) else 0.0)
            ),
            "output_type_match": (
                0.5 if not output_type else (1.0 if output_type in out_types else 0.0)
            ),
            "tool_match": _fraction_present(tools, set(entity.tool_tags or []), default=0.5),
            "install_popularity": _log_popularity(entity.install_count or 0),
            "freshness": _gauss_freshness(entity.created_at),
        }

    if spec.target_entity_type == "skill_pack":
        # Fold soft/preferred keys into the teach-match signal, same as the
        # workflow_pack path above. R14 demotes extracted required caps to
        # preferred, so reading ONLY required_capabilities made this
        # 0.35-weight signal a constant 1.0 for every survivor in the common
        # extraction/brief flow (and emitted a false 'Teaches the required
        # capabilities' reason chip). Soft keys never gate S2 — this is S3
        # scoring only.
        requested_caps = (
            (requirement.get("required_capabilities") or [])
            # Extracted (soft) caps arrive MERGED into preferred_capabilities
            # (build_match_requirement demotes them there) — no _soft_* key
            # for capabilities exists
            + (requirement.get("preferred_capabilities") or [])
        )
        caps = set(entity.capability_tags or [])
        scenario = requirement.get("scenario")
        # Scoring may use extracted (soft) budgets — only hard filters can't (R14)
        time_budget = requirement.get("time_budget") or requirement.get("_soft_time_budget")
        est = entity.estimated_minutes
        if isinstance(time_budget, int | float) and time_budget > 0 and est:
            time_fit = max(
                0.0, 1.0 if est <= time_budget else min(time_budget / est, 1.0)
            )
        else:
            time_fit = 0.5
        difficulty = requirement.get("difficulty") or requirement.get("_soft_difficulty")
        return {
            "capability_teach_match": _fraction_present(requested_caps, caps),
            "difficulty_fit": _difficulty_fit(difficulty, entity.difficulty),
            "scenario_match": (
                0.5 if not scenario else (1.0 if scenario in (entity.scenario_tags or []) else 0.0)
            ),
            "time_fit": time_fit,
            "popularity": _log_popularity(entity.install_count or 0),
        }

    if spec.target_entity_type == "project_template":
        scenario = requirement.get("scenario")
        difficulty_val = (
            entity.difficulty.value
            if hasattr(entity.difficulty, "value")
            else entity.difficulty
        )
        return {
            "scenario_match": (
                0.5 if not scenario else (1.0 if scenario == entity.project_type else 0.0)
            ),
            "difficulty_fit": _difficulty_fit(
                requirement.get("difficulty") or requirement.get("_soft_difficulty"),
                difficulty_val,
            ),
        }

    raise ValueError(f"Unknown target entity type: {spec.target_entity_type}")


async def _creator_signals(
    db: AsyncSession, survivors: list[dict], spec, requirement: dict
) -> list[tuple[dict, dict[str, float]]]:
    """Batch-compute creator signals (evidence, recency, rubric, commercial)."""
    user_ids = [c["id"] for c in survivors]
    if not user_ids:
        return []
    required_caps = requirement.get("required_capabilities") or []

    # Evidence rows in bulk
    evidence_r = await db.execute(
        select(CreatorCapabilityEvidence).where(
            CreatorCapabilityEvidence.org_id == spec.org_id,
            CreatorCapabilityEvidence.user_id.in_(user_ids),
        )
    )
    evidence_by_user: dict[str, list] = {}
    for row in evidence_r.scalars().all():
        evidence_by_user.setdefault(row.user_id, []).append(row)

    # Rubric averages (approved submission reviews) in bulk
    rubric_r = await db.execute(
        select(Submission.user_id, func.avg(SubmissionReview.score))
        .join(SubmissionReview, SubmissionReview.submission_id == Submission.id)
        .where(
            Submission.org_id == spec.org_id,
            Submission.user_id.in_(user_ids),
            SubmissionReview.status == ReviewStatus.APPROVED,
            SubmissionReview.score.isnot(None),
        )
        .group_by(Submission.user_id)
    )
    rubric_avg = {row[0]: float(row[1]) for row in rubric_r.all()}

    # Commercial history (accepted brief applications) in bulk — scoped to
    # THIS org via the brief join. BriefApplication has no org_id column, so
    # an unscoped query would leak a creator's accepted briefs from OTHER
    # orgs into the score (and emit a false "verified" reason). Cross-org
    # data must never enter scoring (S1 privacy / creator-fairness red line).
    commercial_r = await db.execute(
        select(BriefApplication.user_id, func.count())
        .join(ClientBrief, ClientBrief.id == BriefApplication.brief_id)
        .where(
            ClientBrief.org_id == spec.org_id,
            BriefApplication.user_id.in_(user_ids),
            BriefApplication.status == ApplicationStatus.ACCEPTED,
        )
        .group_by(BriefApplication.user_id)
    )
    commercial_count = {row[0]: row[1] for row in commercial_r.all()}

    out: list[tuple[dict, dict[str, float]]] = []
    for cand in survivors:
        uid = cand["id"]
        rows = evidence_by_user.get(uid, [])

        # capability_evidence with Bayesian shrinkage per required capability
        if required_caps:
            cap_scores = []
            for cap in required_caps:
                cap_rows = [r for r in rows if r.capability_key == cap]
                n = len(cap_rows)
                if n == 0:
                    cap_scores.append(0.0)
                    continue
                vals = []
                for r in cap_rows:
                    base = float(r.score) / 100.0 if r.score is not None else 1.0
                    vals.append(min(float(r.weight) * base, 1.0))
                raw_mean = sum(vals) / n
                shrunk = (n / (n + 3)) * raw_mean + (3 / (n + 3)) * 0.5
                cap_scores.append(shrunk)
            capability_evidence = sum(cap_scores) / len(cap_scores)
        else:
            # No specific requirement: overall evidence volume, shrunk
            n = len(rows)
            if n == 0:
                capability_evidence = 0.5
            else:
                vals = [
                    min(float(r.weight) * (float(r.score) / 100.0 if r.score is not None else 1.0), 1.0)
                    for r in rows
                ]
                raw_mean = sum(vals) / n
                capability_evidence = (n / (n + 3)) * raw_mean + (3 / (n + 3)) * 0.5

        # recency: exp decay half-life 90 days on last_login_at
        last_login = cand.get("last_login_at")
        if last_login is None:
            recency = 0.0
        else:
            ref = last_login if last_login.tzinfo else last_login.replace(tzinfo=UTC)
            days = max((_now() - ref).total_seconds() / 86400.0, 0.0)
            recency = math.pow(0.5, days / 90.0)

        avg = rubric_avg.get(uid)
        rubric = min(avg / 100.0, 1.0) if avg is not None else 0.5

        commercial = _log_popularity(commercial_count.get(uid, 0), ceiling=5)

        out.append(
            (
                cand,
                {
                    "capability_evidence": capability_evidence,
                    "recency": recency,
                    "rubric_avg": rubric,
                    "commercial_history": commercial,
                },
            )
        )
    return out

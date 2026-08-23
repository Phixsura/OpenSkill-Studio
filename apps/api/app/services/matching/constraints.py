"""S2 — hard constraints. Failures are distinguishable from low ranking.

LLM/semantic stages can NEVER bypass these: they run strictly upstream and
excluded candidates never reach scoring (D2).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.composer import CreatorCapabilityEvidence

_DIFFICULTY_ORDINAL = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}


async def apply_hard_constraints(
    db: AsyncSession, candidates: list, spec
) -> tuple[list, list[dict]]:
    """Return (survivors, excluded). excluded: [{entity_id, name, failures: [...]}]."""
    requirement = spec.requirement or {}
    survivors: list = []
    excluded: list[dict] = []

    if spec.target_entity_type in ("workflow_pack", "skill_pack"):
        required_caps = requirement.get("required_capabilities") or []
        output_type = requirement.get("output_type")
        user_level = requirement.get("difficulty")

        for pack in candidates:
            failures: list[dict] = []
            pack_caps = set(pack.capability_tags or [])
            for cap in required_caps:
                if cap not in pack_caps:
                    failures.append(
                        {
                            "code": "CAPABILITY_MISSING",
                            "capability": cap,
                            "detail": f"Pack does not provide capability '{cap}'",
                        }
                    )
            if spec.target_entity_type == "workflow_pack" and output_type:
                out_types = {o.get("type") for o in (pack.output_schema or [])}
                if output_type not in out_types:
                    failures.append(
                        {
                            "code": "OUTPUT_TYPE_MISMATCH",
                            "detail": f"Pack does not produce output type '{output_type}'",
                        }
                    )
            if (
                spec.target_entity_type == "skill_pack"
                and user_level
                and pack.difficulty
                and user_level in _DIFFICULTY_ORDINAL
                and pack.difficulty in _DIFFICULTY_ORDINAL
                and _DIFFICULTY_ORDINAL[pack.difficulty] > _DIFFICULTY_ORDINAL[user_level] + 1
            ):
                failures.append(
                    {
                        "code": "DIFFICULTY_TOO_HIGH",
                        "detail": (
                            f"Pack difficulty '{pack.difficulty}' exceeds learner "
                            f"level '{user_level}' by more than one step"
                        ),
                    }
                )
            if failures:
                excluded.append({"entity_id": pack.id, "name": pack.name, "failures": failures})
            else:
                survivors.append(pack)
        return survivors, excluded

    if spec.target_entity_type == "creator":
        required_caps = requirement.get("required_capabilities") or []
        if not required_caps:
            return list(candidates), []
        user_ids = [c["id"] for c in candidates]
        evidence_r = await db.execute(
            select(
                CreatorCapabilityEvidence.user_id,
                CreatorCapabilityEvidence.capability_key,
            ).where(
                CreatorCapabilityEvidence.org_id == spec.org_id,
                CreatorCapabilityEvidence.user_id.in_(user_ids),
                CreatorCapabilityEvidence.capability_key.in_(required_caps),
            )
        )
        verified: dict[str, set[str]] = {}
        for user_id, cap in evidence_r.all():
            verified.setdefault(user_id, set()).add(cap)
        for cand in candidates:
            missing = [cap for cap in required_caps if cap not in verified.get(cand["id"], set())]
            if missing:
                excluded.append(
                    {
                        "entity_id": cand["id"],
                        "name": cand["display_name"],
                        "failures": [
                            {
                                "code": "CAPABILITY_UNVERIFIED",
                                "capability": cap,
                                "detail": f"No verified evidence for '{cap}'",
                            }
                            for cap in missing
                        ],
                    }
                )
            else:
                survivors.append(cand)
        return survivors, excluded

    # project_template: no hard constraints in v1
    return list(candidates), []

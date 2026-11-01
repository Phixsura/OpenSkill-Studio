"""The ONLY trust-plane import surface for product code.

Product services/routers call these functions; they must never import
`app.trustplane.models` / `app.trustplane.services` directly, so the
trust domain can evolve without rippling through the product layer.

Functions are thin delegations — the real logic lives in
app/trustplane/services/*. Each is filled in by its owning phase:

  P1  register_ai_system, get_ai_system, list_ai_systems,
      assess_risk, submit_assessment, approve_assessment,
      get_system_risk_tier, record_trust_audit
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.trustplane.models.inventory import AISystem, RiskTier
    from app.trustplane.models.risk import RiskAssessment


async def register_ai_system(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> AISystem:
    """Register a new AI system in the inventory (P1)."""
    from app.trustplane.services.inventory import create_system as _impl

    return await _impl(db, org_id, user_id, **data)


async def get_ai_system(
    db: AsyncSession, system_id: str, org_id: str
) -> AISystem:
    """Retrieve an AI system by ID and org (P1)."""
    from app.trustplane.services.inventory import get_system as _impl

    return await _impl(db, system_id, org_id)


async def list_ai_systems(
    db: AsyncSession, org_id: str, **filters
) -> tuple[list[AISystem], int]:
    """List AI systems for an org with optional filters (P1)."""
    from app.trustplane.services.inventory import list_systems as _impl

    return await _impl(db, org_id, **filters)


async def assess_risk(
    db: AsyncSession, system_id: str, org_id: str, user_id: str, **data
) -> RiskAssessment:
    """Create a new risk assessment for a system (P1)."""
    from app.trustplane.services.risk import create_assessment as _impl

    return await _impl(db, system_id, org_id, user_id, **data)


async def submit_assessment(
    db: AsyncSession, assessment_id: str, org_id: str, user_id: str
) -> RiskAssessment:
    """Submit a draft assessment for review (P1)."""
    from app.trustplane.services.risk import submit_assessment as _impl

    return await _impl(db, assessment_id, org_id, user_id)


async def approve_assessment(
    db: AsyncSession, assessment_id: str, org_id: str, reviewer_id: str
) -> RiskAssessment:
    """Approve a submitted assessment (P1)."""
    from app.trustplane.services.risk import approve_assessment as _impl

    return await _impl(db, assessment_id, org_id, reviewer_id)


async def get_system_risk_tier(
    db: AsyncSession, system_id: str, org_id: str
) -> RiskTier | None:
    """Return the current risk tier for a system, or None (P1)."""
    from app.trustplane.services.inventory import get_system as _impl

    system = await _impl(db, system_id, org_id)
    return system.risk_tier


async def record_trust_audit(db: AsyncSession, **kwargs) -> None:
    """Append an immutable trust audit event (P1)."""
    from app.trustplane.services.audit import record_trust_audit as _impl

    await _impl(db, **kwargs)

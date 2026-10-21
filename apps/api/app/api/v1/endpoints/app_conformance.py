"""Conformance test suite endpoint — validate app compliance."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse
from app.services import developer as dev_svc
from app.services.conformance import run_conformance_checks

router = APIRouter(tags=["App Conformance"])


@router.get(
    "/developer/apps/{app_id}/conformance",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def run_conformance_suite(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Run the full conformance test suite on an app.

    Checks: manifest validity, version health, installation health,
    sandbox error rate, API key hygiene, event subscriptions, security posture.
    """
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    report = await run_conformance_checks(db, app_id)
    return DataResponse(data=report.to_dict())

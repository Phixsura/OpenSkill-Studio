"""Local development & testing tools for app developers (Part K).

Provides fixture generation, test event sending, and mock provider helpers
so developers can test their apps without production infrastructure.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.services import developer as dev_svc
from app.services.event_dispatch import CANONICAL_EVENTS, emit_event
from app.services.manifest_validator import validate_manifest

router = APIRouter(tags=["Developer Tools"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Test Event Sender ────────────────────────────────────


class SendTestEventRequest(BaseModel):
    event_type: str
    data: dict = {}
    org_id: str


@router.post(
    "/developer/tools/send-test-event",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def send_test_event(
    body: SendTestEventRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a test event to trigger subscribed app webhooks/automation.

    Requires a developer account and org membership. Only delivers to
    installations of apps owned by the caller's developer account.
    """
    # Require developer account
    account = await dev_svc.get_developer_account_by_user(db, user.id)
    if not account:
        raise dev_svc.DeveloperNotFoundError(
            message="You must create a developer account to use dev tools"
        )

    # Require org membership
    await require_org_member(body.org_id, user, db, *ADMIN_ROLES)

    # Validate event type
    if body.event_type not in CANONICAL_EVENTS:
        raise AppError(
            "INVALID_EVENT_TYPE",
            f"Unknown event type: {body.event_type}",
            422,
        )

    deliveries = await emit_event(
        db,
        event_type=body.event_type,
        data={**body.data, "_test": True},
        org_id=body.org_id,
        user_id=user.id,
    )
    await db.commit()
    return DataResponse(
        data={
            "event_type": body.event_type,
            "deliveries": deliveries,
            "test": True,
        }
    )


# ── Event Types Reference ───────────────────────────────


@router.get(
    "/developer/tools/event-types",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_event_types(
    user: User = Depends(get_current_user),
):
    """List all canonical platform event types."""
    categorized: dict[str, list[str]] = {}
    for event in sorted(CANONICAL_EVENTS):
        category = event.split(".")[0]
        categorized.setdefault(category, []).append(event)
    return DataResponse(
        data={
            "total": len(CANONICAL_EVENTS),
            "categories": categorized,
        }
    )


# ── Fixture Generator ───────────────────────────────────


@router.post(
    "/developer/tools/generate-fixtures",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def generate_test_fixtures(
    user: User = Depends(get_current_user),
):
    """Generate sample fixture data for local development.

    Returns mock data structures matching platform API responses.
    """
    return DataResponse(
        data={
            "cohort": {
                "id": "01FIXTURE_COHORT_001",
                "name": "Test Cohort Alpha",
                "description": "A fixture cohort for local development",
                "status": "active",
                "member_count": 25,
            },
            "project": {
                "id": "01FIXTURE_PROJECT_001",
                "name": "Test Project",
                "description": "A fixture project for testing submissions",
                "status": "published",
                "deliverable_count": 3,
            },
            "submission": {
                "id": "01FIXTURE_SUBMIT_001",
                "project_id": "01FIXTURE_PROJECT_001",
                "status": "completed",
                "grade": 85,
                "submitted_at": "2026-10-22T12:00:00Z",
            },
            "user": {
                "id": "01FIXTURE_USER_001",
                "email": "test-user@example.com",
                "display_name": "Test User",
                "role": "student",
            },
            "organization": {
                "id": "01FIXTURE_ORG_001",
                "name": "Test Organization",
                "slug": "test-org",
                "status": "active",
            },
            "event_payload": {
                "submission.completed": {
                    "submission_id": "01FIXTURE_SUBMIT_001",
                    "project_id": "01FIXTURE_PROJECT_001",
                    "user_id": "01FIXTURE_USER_001",
                    "grade": 85,
                    "completed_at": "2026-10-22T12:00:00Z",
                },
                "cohort.member_added": {
                    "cohort_id": "01FIXTURE_COHORT_001",
                    "user_id": "01FIXTURE_USER_001",
                    "role": "student",
                    "added_at": "2026-10-22T12:00:00Z",
                },
                "pack.published": {
                    "pack_id": "01FIXTURE_PACK_001",
                    "name": "Test Skill Pack",
                    "version": "1.0.0",
                    "visibility": "public",
                },
            },
        }
    )


# ── Manifest Validator (CLI-compatible) ──────────────────


class QuickValidateRequest(BaseModel):
    manifest: dict


@router.post(
    "/developer/tools/validate",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def quick_validate(
    body: QuickValidateRequest,
    user: User = Depends(get_current_user),
):
    """Quick manifest validation — same as POST /developer/validate-manifest
    but grouped under /tools for discoverability."""
    result = validate_manifest(body.manifest)
    return DataResponse(data=result.to_dict())


# ── Permission Checker ───────────────────────────────────


@router.get(
    "/developer/tools/permissions",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_all_permissions(
    user: User = Depends(get_current_user),
):
    """List all valid permission scopes with descriptions."""
    from app.services.manifest_validator import VALID_PERMISSIONS

    scopes: dict[str, list[str]] = {}
    for perm in sorted(VALID_PERMISSIONS):
        category = perm.split(":")[0]
        scopes.setdefault(category, []).append(perm)
    return DataResponse(
        data={
            "total": len(VALID_PERMISSIONS),
            "categories": scopes,
        }
    )


# ── UI Surface Reference ────────────────────────────────


@router.get(
    "/developer/tools/ui-surfaces",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_ui_surfaces(
    user: User = Depends(get_current_user),
):
    """List available UI extension surfaces."""
    from app.services.manifest_validator import VALID_SURFACES

    surfaces = [
        {"id": "dashboard_card", "label": "Dashboard Card", "max_width": 400, "max_height": 300},
        {"id": "project_sidebar", "label": "Project Sidebar", "max_width": 320, "max_height": None},
        {"id": "cohort_tool", "label": "Cohort Tool", "max_width": 800, "max_height": 600},
        {"id": "submission_panel", "label": "Submission Panel", "max_width": 400, "max_height": None},
        {"id": "registry_detail", "label": "Registry Detail", "max_width": 800, "max_height": 400},
        {"id": "settings_page", "label": "Settings Page", "max_width": None, "max_height": None},
        {"id": "client_portal_widget", "label": "Client Portal Widget", "max_width": 600, "max_height": 400},
        {"id": "operator_console", "label": "Operator Console", "max_width": 800, "max_height": 600},
    ]
    return DataResponse(data={"surfaces": surfaces, "total": len(VALID_SURFACES)})

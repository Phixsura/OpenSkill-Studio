"""Event hooks — emit developer platform events from core platform operations.

These functions are called from service/endpoint layers to emit events
that subscribed apps will receive via webhooks or automation rules.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.event_dispatch import emit_event

log = structlog.get_logger()


async def on_submission_completed(
    db: AsyncSession,
    *,
    submission_id: str,
    project_id: str,
    user_id: str,
    org_id: str,
    grade: float | None = None,
) -> int:
    """Emit submission.completed event."""
    return await emit_event(
        db,
        "submission.completed",
        {
            "submission_id": submission_id,
            "project_id": project_id,
            "user_id": user_id,
            "grade": grade,
        },
        org_id=org_id,
        user_id=user_id,
    )


async def on_submission_graded(
    db: AsyncSession,
    *,
    submission_id: str,
    project_id: str,
    user_id: str,
    org_id: str,
    grade: float,
    graded_by: str | None = None,
) -> int:
    """Emit submission.graded event."""
    return await emit_event(
        db,
        "submission.graded",
        {
            "submission_id": submission_id,
            "project_id": project_id,
            "user_id": user_id,
            "grade": grade,
            "graded_by": graded_by,
        },
        org_id=org_id,
        user_id=user_id,
    )


async def on_cohort_member_added(
    db: AsyncSession,
    *,
    cohort_id: str,
    user_id: str,
    org_id: str,
    role: str = "student",
) -> int:
    """Emit cohort.member_added event."""
    return await emit_event(
        db,
        "cohort.member_added",
        {
            "cohort_id": cohort_id,
            "user_id": user_id,
            "role": role,
        },
        org_id=org_id,
        user_id=user_id,
    )


async def on_cohort_member_removed(
    db: AsyncSession,
    *,
    cohort_id: str,
    user_id: str,
    org_id: str,
) -> int:
    """Emit cohort.member_removed event."""
    return await emit_event(
        db,
        "cohort.member_removed",
        {
            "cohort_id": cohort_id,
            "user_id": user_id,
        },
        org_id=org_id,
        user_id=user_id,
    )


async def on_project_published(
    db: AsyncSession,
    *,
    project_id: str,
    org_id: str,
    published_by: str,
) -> int:
    """Emit project.published event."""
    return await emit_event(
        db,
        "project.published",
        {
            "project_id": project_id,
            "published_by": published_by,
        },
        org_id=org_id,
        user_id=published_by,
    )


async def on_pack_published(
    db: AsyncSession,
    *,
    pack_id: str,
    name: str,
    version: str,
    org_id: str,
    published_by: str,
) -> int:
    """Emit pack.published event."""
    return await emit_event(
        db,
        "pack.published",
        {
            "pack_id": pack_id,
            "name": name,
            "version": version,
        },
        org_id=org_id,
        user_id=published_by,
    )


async def on_pack_installed(
    db: AsyncSession,
    *,
    pack_id: str,
    org_id: str,
    installed_by: str,
) -> int:
    """Emit pack.installed event."""
    return await emit_event(
        db,
        "pack.installed",
        {
            "pack_id": pack_id,
            "installed_by": installed_by,
        },
        org_id=org_id,
        user_id=installed_by,
    )


async def on_workflow_run_completed(
    db: AsyncSession,
    *,
    run_id: str,
    workflow_pack_id: str,
    org_id: str,
    status: str = "completed",
) -> int:
    """Emit workflow.run_completed or workflow.run_failed event."""
    event_type = "workflow.run_completed" if status == "completed" else "workflow.run_failed"
    return await emit_event(
        db,
        event_type,
        {
            "run_id": run_id,
            "workflow_pack_id": workflow_pack_id,
            "status": status,
        },
        org_id=org_id,
    )


async def on_app_installed(
    db: AsyncSession,
    *,
    app_id: str,
    installation_id: str,
    org_id: str,
    installed_by: str,
) -> int:
    """Emit app.installed event."""
    return await emit_event(
        db,
        "app.installed",
        {
            "app_id": app_id,
            "installation_id": installation_id,
            "installed_by": installed_by,
        },
        org_id=org_id,
        user_id=installed_by,
    )


async def on_app_uninstalled(
    db: AsyncSession,
    *,
    app_id: str,
    installation_id: str,
    org_id: str,
) -> int:
    """Emit app.uninstalled event."""
    return await emit_event(
        db,
        "app.uninstalled",
        {
            "app_id": app_id,
            "installation_id": installation_id,
        },
        org_id=org_id,
    )


async def on_evaluation_completed(
    db: AsyncSession,
    *,
    evaluation_id: str,
    submission_id: str,
    org_id: str,
    result: str = "completed",
) -> int:
    """Emit evaluation.completed or evaluation.failed event."""
    event_type = "evaluation.completed" if result == "completed" else "evaluation.failed"
    return await emit_event(
        db,
        event_type,
        {
            "evaluation_id": evaluation_id,
            "submission_id": submission_id,
            "result": result,
        },
        org_id=org_id,
    )


async def on_org_member_added(
    db: AsyncSession,
    *,
    org_id: str,
    user_id: str,
    role: str,
    added_by: str,
) -> int:
    """Emit org.member_added event."""
    return await emit_event(
        db,
        "org.member_added",
        {
            "user_id": user_id,
            "role": role,
            "added_by": added_by,
        },
        org_id=org_id,
        user_id=added_by,
    )

"""Third-party adapter and source registry endpoints."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse
from app.services.adapter_sdk import (
    get_adapter,
    get_source,
    list_adapters,
    list_sources,
)

router = APIRouter(tags=["Adapter Registry"])


@router.get(
    "/developer/adapters",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_registered_adapters(
    user: User = Depends(get_current_user),
):
    """List all registered third-party provider adapters."""
    adapters = list_adapters()
    return DataResponse(
        data=[
            {
                "name": a.name,
                "display_name": a.display_name,
                "version": a.version,
                "capabilities": a.capabilities,
                "retry_policy": a.retry_policy,
                "idempotent": a.idempotent,
                "health_check_supported": a.health_check_supported,
            }
            for a in adapters
        ]
    )


@router.get(
    "/developer/adapters/{adapter_name}",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_adapter_detail(
    adapter_name: str,
    user: User = Depends(get_current_user),
):
    """Get details for a specific adapter."""
    adapter = get_adapter(adapter_name)
    if not adapter:
        from app.exceptions import AppError

        raise AppError("ADAPTER_NOT_FOUND", f"Adapter '{adapter_name}' not found", 404)
    meta = adapter.get_metadata()
    return DataResponse(
        data={
            "name": meta.name,
            "display_name": meta.display_name,
            "version": meta.version,
            "capabilities": meta.capabilities,
            "retry_policy": meta.retry_policy,
            "idempotent": meta.idempotent,
            "health_check_supported": meta.health_check_supported,
        }
    )


@router.get(
    "/developer/adapters/{adapter_name}/health",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def check_adapter_health(
    adapter_name: str,
    user: User = Depends(get_current_user),
):
    """Run health check on an adapter."""
    adapter = get_adapter(adapter_name)
    if not adapter:
        from app.exceptions import AppError

        raise AppError("ADAPTER_NOT_FOUND", f"Adapter '{adapter_name}' not found", 404)
    health = await adapter.health_check()
    return DataResponse(
        data={
            "status": health.status,
            "latency_ms": health.latency_ms,
            "message": health.message,
            "checked_at": health.checked_at,
        }
    )


@router.get(
    "/developer/sources",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_registered_sources(
    user: User = Depends(get_current_user),
):
    """List all registered third-party ecosystem source adapters."""
    sources = list_sources()
    return DataResponse(data=sources)


@router.get(
    "/developer/sources/{source_name}",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_source_detail(
    source_name: str,
    user: User = Depends(get_current_user),
):
    """Get details for a specific source adapter."""
    source = get_source(source_name)
    if not source:
        from app.exceptions import AppError

        raise AppError("SOURCE_NOT_FOUND", f"Source '{source_name}' not found", 404)
    return DataResponse(data=source.get_metadata())


@router.get(
    "/developer/sources/{source_name}/health",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def check_source_health(
    source_name: str,
    user: User = Depends(get_current_user),
):
    """Run health check on a source adapter."""
    source = get_source(source_name)
    if not source:
        from app.exceptions import AppError

        raise AppError("SOURCE_NOT_FOUND", f"Source '{source_name}' not found", 404)
    health = await source.health_check()
    return DataResponse(
        data={
            "status": health.status,
            "latency_ms": health.latency_ms,
            "message": health.message,
            "checked_at": health.checked_at,
        }
    )

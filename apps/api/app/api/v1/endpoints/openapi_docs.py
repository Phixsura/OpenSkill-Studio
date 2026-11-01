"""OpenAPI spec endpoint for the Developer Platform public API.

Provides a filtered OpenAPI schema containing only the developer-facing
endpoints, suitable for SDK generation and documentation portals.
"""

from fastapi import APIRouter, Depends
from fastapi.openapi.utils import get_openapi

from app.core.rate_limit import rate_limit

router = APIRouter(tags=["API Documentation"])


@router.get(
    "/developer/openapi.json",
    dependencies=[Depends(rate_limit(30, 60))],
    include_in_schema=False,
)
async def get_developer_openapi():
    """Get OpenAPI spec for developer-facing endpoints only.

    Filters the full OpenAPI schema to include only:
    - /developer/* endpoints
    - /marketplace/* endpoints
    - /oauth/* endpoints
    - /orgs/{org_id}/apps/* endpoints

    Useful for SDK code generation and developer documentation.
    """
    from app.main import app

    full_schema = get_openapi(
        title="OpenSkill Developer Platform API",
        version="1.0.0",
        description="Public API for building apps, connectors, and extensions on OpenSkill Studio.",
        routes=app.routes,
    )

    # Filter to developer-facing paths
    dev_prefixes = (
        "/api/v1/developer/",
        "/api/v1/marketplace/",
        "/api/v1/oauth/",
        "/api/v1/orgs/{org_id}/apps/",
    )

    filtered_paths = {}
    for path, operations in full_schema.get("paths", {}).items():
        if any(path.startswith(prefix) for prefix in dev_prefixes):
            filtered_paths[path] = operations

    full_schema["paths"] = filtered_paths
    full_schema["info"]["title"] = "OpenSkill Developer Platform API"
    full_schema["info"]["description"] = (
        "Build apps, connectors, and extensions for OpenSkill Studio. "
        "Authenticate with `Bearer osk_app_...` API key or OAuth2 access token."
    )

    return full_schema

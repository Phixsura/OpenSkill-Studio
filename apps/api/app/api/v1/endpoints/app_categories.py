"""App category reference endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.models.developer import AppStatus, AppVisibility, DeveloperApp
from app.schemas.base import DataResponse

router = APIRouter(tags=["App Categories"])

CATEGORY_METADATA = {
    "connector": {
        "icon": "🔌",
        "label": "Connectors",
        "description": "LMS, HRIS, CRM, and SIS integrations",
    },
    "workflow_adapter": {
        "icon": "⚡",
        "label": "Workflow Adapters",
        "description": "AI provider adapters for workflow execution",
    },
    "ui_extension": {
        "icon": "🖥️",
        "label": "UI Extensions",
        "description": "Dashboard cards, sidebars, and panels",
    },
    "analytics": {
        "icon": "📊",
        "label": "Analytics",
        "description": "Reporting, insights, and data export tools",
    },
    "automation": {
        "icon": "🤖",
        "label": "Automation",
        "description": "Event-driven workflows and integrations",
    },
    "content_pack": {
        "icon": "📦",
        "label": "Content Packs",
        "description": "Skill and workflow content bundles",
    },
    "ecosystem_source": {
        "icon": "🌐",
        "label": "Ecosystem Sources",
        "description": "External data source adapters",
    },
}


@router.get(
    "/marketplace/categories",
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """List all app categories with metadata and app counts."""
    # Count published apps per category
    result = await db.execute(
        select(
            DeveloperApp.category,
            func.count().label("count"),
        )
        .where(
            DeveloperApp.status == AppStatus.PUBLISHED,
            DeveloperApp.visibility == AppVisibility.PUBLIC,
        )
        .group_by(DeveloperApp.category)
    )
    counts = {
        row.category.value if hasattr(row.category, "value") else row.category: row.count
        for row in result.all()
    }

    categories = []
    for key, meta in CATEGORY_METADATA.items():
        categories.append({
            "key": key,
            "icon": meta["icon"],
            "label": meta["label"],
            "description": meta["description"],
            "app_count": counts.get(key, 0),
        })

    return DataResponse(data=categories)

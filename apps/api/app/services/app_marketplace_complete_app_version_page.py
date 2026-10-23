"""Complete app version page — version management with publish, rollback, and diff."""


def build_complete_version_page(*, app: dict, versions: list[dict], current: dict | None,
                                     pipeline: dict | None) -> dict:
    published = [v for v in versions if v.get("status") == "published"]
    in_review = [v for v in versions if v.get("status") == "in_review"]
    return {
        "page_type": "version_management",
        "app": {"id": app["id"], "name": app["name"]},
        "current_version": current,
        "versions": versions[:20],
        "stats": {"total": len(versions), "published": len(published), "in_review": len(in_review)},
        "pipeline": pipeline,
        "actions": [
            {"id": "new_version", "label": "Create New Version", "icon": "🆕", "primary": True},
            {"id": "compare", "label": "Compare Versions", "icon": "🔄"},
        ],
    }

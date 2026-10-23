"""Complete install page — the master aggregator for the entire app installation experience."""


def build_complete_install_page(*, app: dict, developer: dict, install_guard: dict,
                                    permissions: dict, config_schema: dict | None,
                                    reviews_summary: dict, related_apps: list[dict]) -> dict:
    return {
        "page_type": "complete_install",
        "hero": {"app_name": app["name"], "developer_name": developer.get("display_name"),
                  "developer_verified": developer.get("verified", False),
                  "rating": reviews_summary.get("avg_rating", 0),
                  "install_count": reviews_summary.get("install_count", 0)},
        "guard": {"can_install": install_guard.get("can_install", True),
                   "blockers": install_guard.get("blockers", []),
                   "warnings": install_guard.get("warnings", [])},
        "steps": [
            {"key": "review_permissions", "title": "Review Permissions",
             "data": permissions, "required": True},
        ] + ([{"key": "configure", "title": "Configure", "data": config_schema, "required": False}]
             if config_schema else []) + [
            {"key": "confirm", "title": "Confirm & Install", "required": True},
        ],
        "sidebar": {
            "reviews": reviews_summary,
            "related_apps": related_apps[:4],
        },
        "cta": {"label": "Install" if install_guard.get("can_install") else "Cannot Install",
                "enabled": install_guard.get("can_install", True)},
    }

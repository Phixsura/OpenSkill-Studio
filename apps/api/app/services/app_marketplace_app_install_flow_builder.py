"""Install flow builder — compile complete install flow page data."""

def build_install_flow_page(*, app: dict, permissions: list[str], org: dict,
                              config_schema: dict | None, quick_install: bool) -> dict:
    return {
        "app": {"name": app.get("name"), "slug": app.get("slug"), "category": app.get("category")},
        "org": {"name": org.get("name"), "id": org.get("id")},
        "permissions": permissions,
        "permission_count": len(permissions),
        "has_config": config_schema is not None,
        "config_schema": config_schema,
        "quick_install": quick_install,
        "flow_type": "quick" if quick_install else "standard",
    }

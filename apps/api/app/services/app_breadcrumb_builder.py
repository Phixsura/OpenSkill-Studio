"""Breadcrumb builder — generate breadcrumbs for any developer platform page."""

ROUTES = {
    "developer": [{"label": "Dashboard", "href": "/dashboard"}, {"label": "Developer", "href": "/dashboard/developer"}],
    "apps": [{"label": "Dashboard", "href": "/dashboard"}, {"label": "Developer", "href": "/dashboard/developer"}, {"label": "Apps", "href": "/dashboard/developer/apps"}],
    "marketplace": [{"label": "Marketplace", "href": "/marketplace"}],
    "marketplace_app": lambda slug, name: [{"label": "Marketplace", "href": "/marketplace"}, {"label": "Apps", "href": "/marketplace/apps"}, {"label": name}],
}


def build_breadcrumbs(route: str, **kwargs) -> list[dict]:
    builder = ROUTES.get(route, [])
    if callable(builder):
        return builder(**kwargs)
    return list(builder)

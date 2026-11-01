"""Router route count verification — each router has minimum routes."""

import pytest
from app.api.v1.endpoints import (
    developer_accounts, developer_apps, app_installations,
    app_review, app_marketplace, app_sandbox, app_observability,
    app_conformance, app_export, app_admin, app_batch,
    app_categories, app_version_ops, dev_sandbox_tools,
    webhook_deliveries, oauth,
)

ROUTERS_WITH_MIN_ROUTES = [
    ("developer_accounts", developer_accounts, 2),
    ("developer_apps", developer_apps, 3),
    ("app_installations", app_installations, 2),
    ("app_review", app_review, 2),
    ("app_marketplace", app_marketplace, 2),
    ("app_sandbox", app_sandbox, 1),
    ("app_observability", app_observability, 1),
    ("app_conformance", app_conformance, 1),
    ("app_export", app_export, 1),
    ("app_admin", app_admin, 1),
    ("app_batch", app_batch, 1),
    ("app_categories", app_categories, 1),
    ("app_version_ops", app_version_ops, 1),
    ("dev_sandbox_tools", dev_sandbox_tools, 1),
    ("webhook_deliveries", webhook_deliveries, 1),
    ("oauth", oauth, 2),
]

@pytest.mark.parametrize("name,module,min_routes", ROUTERS_WITH_MIN_ROUTES,
    ids=lambda x: x if isinstance(x, str) else (x.__name__ if hasattr(x, '__name__') else str(x)))
def test_minimum_routes(name, module, min_routes):
    count = len(module.router.routes)
    assert count >= min_routes, f"{name} has {count} routes, expected >= {min_routes}"

def test_total_dev_platform_routes():
    total = sum(len(m.router.routes) for _, m, _ in ROUTERS_WITH_MIN_ROUTES)
    assert total >= 30, f"Total routes: {total}, expected >= 30"

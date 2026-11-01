"""Verify all developer platform router modules import and have routes."""

import pytest
from app.api.v1.endpoints import (
    developer_accounts, developer_apps, app_installations,
    app_review, app_marketplace, app_sandbox, app_observability,
    app_conformance, app_export, app_admin, app_batch,
    app_categories, app_version_ops, dev_sandbox_tools,
    webhook_deliveries, oauth,
)

ROUTERS = [
    ("developer_accounts", developer_accounts),
    ("developer_apps", developer_apps),
    ("app_installations", app_installations),
    ("app_review", app_review),
    ("app_marketplace", app_marketplace),
    ("app_sandbox", app_sandbox),
    ("app_observability", app_observability),
    ("app_conformance", app_conformance),
    ("app_export", app_export),
    ("app_admin", app_admin),
    ("app_batch", app_batch),
    ("app_categories", app_categories),
    ("app_version_ops", app_version_ops),
    ("dev_sandbox_tools", dev_sandbox_tools),
    ("webhook_deliveries", webhook_deliveries),
    ("oauth", oauth),
]

@pytest.mark.parametrize("name,module", ROUTERS, ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_module_has_router(name, module):
    assert hasattr(module, "router"), f"{name} missing router"

@pytest.mark.parametrize("name,module", ROUTERS, ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_router_has_routes(name, module):
    assert len(module.router.routes) > 0, f"{name} router has no routes"

def test_total_router_count():
    assert len(ROUTERS) == 16

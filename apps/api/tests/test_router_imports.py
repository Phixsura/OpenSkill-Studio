"""Verify every router module is importable and has a router."""

import pytest

ROUTER_MODULES = [
    "app.api.v1.endpoints.adapter_registry",
    "app.api.v1.endpoints.app_admin",
    "app.api.v1.endpoints.app_batch",
    "app.api.v1.endpoints.app_categories",
    "app.api.v1.endpoints.app_conformance",
    "app.api.v1.endpoints.app_export",
    "app.api.v1.endpoints.app_installations",
    "app.api.v1.endpoints.app_marketplace",
    "app.api.v1.endpoints.app_observability",
    "app.api.v1.endpoints.app_review",
    "app.api.v1.endpoints.app_sandbox",
    "app.api.v1.endpoints.app_version_ops",
    "app.api.v1.endpoints.dev_sandbox_tools",
    "app.api.v1.endpoints.developer_accounts",
    "app.api.v1.endpoints.developer_apps",
    "app.api.v1.endpoints.manifest_validation",
    "app.api.v1.endpoints.oauth",
    "app.api.v1.endpoints.openapi_docs",
    "app.api.v1.endpoints.webhook_deliveries",
]

@pytest.mark.parametrize("module_path", ROUTER_MODULES)
def test_router_importable(module_path):
    import importlib
    mod = importlib.import_module(module_path)
    assert hasattr(mod, "router")

def test_router_count():
    assert len(ROUTER_MODULES) == 19

"""Verify every service module is importable."""

import pytest

SERVICE_MODULES = [
    "app.services.adapter_sdk",
    "app.services.app_analytics",
    "app.services.app_compatibility",
    "app.services.app_discovery",
    "app.services.app_event_hooks",
    "app.services.app_export",
    "app.services.app_import",
    "app.services.app_lifecycle",
    "app.services.app_metrics",
    "app.services.app_notifications",
    "app.services.app_permissions",
    "app.services.app_rate_limit",
    "app.services.app_search",
    "app.services.app_usage",
    "app.services.app_webhooks",
    "app.services.conformance",
    "app.services.developer",
    "app.services.event_dispatch",
    "app.services.idempotency",
    "app.services.manifest_validator",
    "app.services.sandbox",
    "app.services.webhook_verify",
]

@pytest.mark.parametrize("module_path", SERVICE_MODULES)
def test_service_importable(module_path):
    import importlib
    mod = importlib.import_module(module_path)
    assert mod is not None

def test_service_count():
    assert len(SERVICE_MODULES) == 22

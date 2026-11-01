"""Service module coverage — ensure all developer platform services importable."""

import pytest
import importlib

SERVICES = [
    "app.services.developer",
    "app.services.sandbox",
    "app.services.event_dispatch",
    "app.services.adapter_sdk",
    "app.services.manifest_validator",
    "app.services.conformance",
    "app.services.app_compatibility",
    "app.services.app_health_monitor",
    "app.services.app_metrics",
    "app.services.app_analytics",
    "app.services.app_lifecycle",
    "app.services.app_notifications",
    "app.services.app_permissions",
    "app.services.app_export",
    "app.services.app_import",
    "app.services.webhook_verify",
    "app.services.idempotency",
    "app.services.app_rate_limit",
    "app.services.app_event_hooks",
    "app.services.app_webhooks",
    "app.services.app_search",
    "app.services.app_discovery",
    "app.services.app_usage",
]

@pytest.mark.parametrize("module_path", SERVICES)
def test_service_importable(module_path):
    mod = importlib.import_module(module_path)
    assert mod is not None

@pytest.mark.parametrize("module_path", SERVICES)
def test_service_has_functions(module_path):
    mod = importlib.import_module(module_path)
    public = [name for name in dir(mod) if not name.startswith("_")]
    assert len(public) > 0, f"{module_path} has no public exports"

def test_total_services():
    assert len(SERVICES) == 23

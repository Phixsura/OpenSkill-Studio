from app.services.app_marketplace_extension_capability_registry import (
    CapabilityRegistryService,
)


def test_declare_and_check():
    svc = CapabilityRegistryService()
    svc.declare("ext-1", [{"name": "chart"}, {"name": "export"}])
    assert svc.has_capability("ext-1", "chart") is True
    assert svc.has_capability("ext-1", "auth") is False


def test_find_providers():
    svc = CapabilityRegistryService()
    svc.declare("ext-1", [{"name": "chart"}])
    svc.declare("ext-2", [{"name": "chart"}, {"name": "export"}])
    svc.declare("ext-3", [{"name": "auth"}])
    providers = svc.find_providers("chart")
    assert providers == ["ext-1", "ext-2"]


def test_check_requirements_satisfied():
    svc = CapabilityRegistryService()
    svc.declare("ext-auth", [{"name": "auth"}])
    svc.declare("ext-app", [], requires=["auth"])
    result = svc.check_requirements("ext-app")
    assert result["satisfied"] is True


def test_check_requirements_missing():
    svc = CapabilityRegistryService()
    svc.declare("ext-app", [], requires=["auth", "billing"])
    result = svc.check_requirements("ext-app")
    assert result["satisfied"] is False
    assert "auth" in result["missing"]
    assert "billing" in result["missing"]


def test_find_compatible():
    svc = CapabilityRegistryService()
    svc.declare("ext-1", [{"name": "chart"}, {"name": "export"}])
    svc.declare("ext-2", [{"name": "chart"}])
    svc.declare("ext-3", [{"name": "chart"}, {"name": "export"}, {"name": "auth"}])
    compatible = svc.find_compatible(["chart", "export"])
    assert compatible == ["ext-1", "ext-3"]


def test_get_capabilities():
    svc = CapabilityRegistryService()
    svc.declare("ext-1", [{"name": "chart", "version": "2.0", "description": "Charting"}])
    caps = svc.get_capabilities("ext-1")
    assert len(caps) == 1
    assert caps[0]["version"] == "2.0"


def test_get_all_capabilities():
    svc = CapabilityRegistryService()
    svc.declare("ext-1", [{"name": "chart"}])
    svc.declare("ext-2", [{"name": "auth"}])
    assert svc.get_all_capabilities() == ["auth", "chart"]


def test_not_registered():
    svc = CapabilityRegistryService()
    assert svc.has_capability("unknown", "x") is False
    assert svc.get_capabilities("unknown") == []

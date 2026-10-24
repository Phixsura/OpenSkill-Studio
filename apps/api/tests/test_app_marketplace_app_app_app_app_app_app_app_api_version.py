from app.services.app_marketplace_app_app_app_app_app_app_app_api_version import ApiVersionManager

def test_version_lifecycle():
    vm = ApiVersionManager()
    vm.register("v1", "active")
    vm.register("v2", "active")
    vm.deprecate("v1", "2027-01-01")
    r = vm.resolve("v1")
    assert r["status"] == "deprecated"
    assert vm.latest() == "v2"

def test_fallback():
    vm = ApiVersionManager()
    vm.register("v1")
    r = vm.resolve("v99")
    assert r["fallback"]
    assert r["resolved"] == "v1"

def test_summary():
    vm = ApiVersionManager()
    vm.register("v1", "active")
    vm.register("v2", "deprecated")
    s = vm.summary()
    assert s["total"] == 2
    assert s["latest"] == "v1"

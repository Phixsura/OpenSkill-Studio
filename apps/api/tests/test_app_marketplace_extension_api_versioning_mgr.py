from app.services.app_marketplace_extension_api_versioning_mgr import ApiVersioningMgrService

def test_register_and_latest():
    svc = ApiVersioningMgrService()
    svc.register("v1", ["Initial"])
    svc.register("v2", ["New endpoints"])
    assert svc.get_latest().version == "v2"
    assert len(svc.get_active()) == 2

def test_deprecate():
    svc = ApiVersioningMgrService()
    svc.register("v1")
    svc.deprecate("v1")
    assert len(svc.get_active()) == 0
    assert svc.is_supported("v1") is True  # deprecated but still supported

def test_sunset():
    svc = ApiVersioningMgrService()
    svc.register("v1")
    svc.sunset("v1")
    assert svc.is_supported("v1") is False

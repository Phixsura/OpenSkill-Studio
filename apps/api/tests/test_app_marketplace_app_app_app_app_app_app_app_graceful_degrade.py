from app.services.app_marketplace_app_app_app_app_app_app_app_graceful_degrade import GracefulDegradation

def test_levels():
    gd = GracefulDegradation()
    gd.register_feature("search", priority=3)
    gd.register_feature("analytics", priority=5)
    gd.register_feature("auth", priority=10)
    r = gd.set_level("reduced")
    assert r["active_features"] == 2  # analytics + auth
    assert not gd.is_active("search")
    assert gd.is_active("auth")

def test_emergency():
    gd = GracefulDegradation()
    gd.register_feature("search", priority=3)
    gd.register_feature("auth", priority=10)
    gd.set_level("emergency")
    assert gd.status()["active"] == 1
    assert gd.status()["shed"] == 1

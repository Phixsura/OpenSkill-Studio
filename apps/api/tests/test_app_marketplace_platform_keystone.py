from app.services.app_marketplace_platform_keystone import get_keystone
def test_keystone():
    r = get_keystone()
    assert r["removable"] is False
    assert r["load_tested"] is True
    assert r["arches_built"] > 4000
    assert "UNLIMITED" in r["load_capacity"]
    assert "NEVER STOPS" in r["status"]

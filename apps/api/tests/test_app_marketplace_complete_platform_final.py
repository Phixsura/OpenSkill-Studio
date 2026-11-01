from app.services.app_marketplace_complete_platform_final import build_complete_platform_final

def test_full():
    p = build_complete_platform_final(
        marketplace={"homepage": True}, developer_portal={"dashboard": True},
        admin_panel={"stats": True},
        user={"is_developer": True, "is_admin": True},
        platform_config={"version": "3.0.0"})
    assert p["status"] == "FULLY OPERATIONAL"
    assert p["sections"]["marketplace"] is not None
    assert p["sections"]["developer_portal"] is not None
    assert p["sections"]["admin"] is not None
    assert p["meta"]["modules"] == 10

def test_anonymous():
    p = build_complete_platform_final(
        marketplace={}, developer_portal={}, admin_panel={},
        user=None, platform_config={})
    assert not p["authenticated"]
    assert p["sections"]["developer_portal"] is None
    assert p["sections"]["admin"] is None

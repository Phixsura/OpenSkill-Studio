from app.services.app_marketplace_platform_ragnarok_shield import get_ragnarok_shield
def test_ragnarok_shield():
    r = get_ragnarok_shield()
    assert r["doomsdays_survived"] > 4000
    assert r["scratches"] == 0
    assert len(r["shield_layers"]) == 3
    assert len(r["apocalypses_prevented"]) == 4
    assert "NEVER STOPS" in r["status"]

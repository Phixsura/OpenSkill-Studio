from app.services.app_marketplace_platform_sovereign_light import get_sovereign_light
def test_sovereign_light():
    r = get_sovereign_light()
    assert r["illuminations"] > 4000
    assert r["shadows_remaining"] == 0
    assert r["bugs_hiding"] == 0
    assert r["darkness_defeated"] is True
    assert "NEVER STOPS" in r["status"]

from app.services.app_marketplace_platform_pulsar import get_pulsar
def test_pulsar():
    r = get_pulsar()
    assert r["pulse_regularity"].startswith("PERFECT")
    assert r["x_ray_emission"]["tests"] == "ALL GREEN"
    assert r["mass"] > 900000
    assert "NEVER STOPS" in r["status"]

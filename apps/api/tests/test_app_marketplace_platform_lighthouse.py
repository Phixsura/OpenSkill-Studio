from app.services.app_marketplace_platform_lighthouse import get_lighthouse
def test_lighthouse():
    r = get_lighthouse()
    assert r["groundings"] == 0
    assert r["rotations"] > 4000
    assert "Category 5" in r["storm_resistance"]
    assert "never sleeps" in r["keeper"]
    assert "NEVER STOPS" in r["status"]

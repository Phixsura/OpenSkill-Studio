from app.services.app_marketplace_app_app_app_app_app_app_app_blue_green import BlueGreenSwitcher

def test_blue_green():
    bg = BlueGreenSwitcher()
    bg.deploy(version="2.0")
    bg.health_check("green", healthy=True)
    r = bg.switch()
    assert r["switched_to"] == "green"
    assert r["version"] == "2.0"
    s = bg.status()
    assert s["active"] == "green"
    assert s["active_version"] == "2.0"

def test_rollback():
    bg = BlueGreenSwitcher()
    bg._slots["blue"]["version"] = "1.0"
    bg._slots["blue"]["status"] = "active"
    bg.deploy(version="2.0")
    bg.health_check("green", healthy=True)
    bg.switch()
    rb = bg.rollback()
    assert rb["rolled_back_to"] == "blue"
    assert rb["version"] == "1.0"

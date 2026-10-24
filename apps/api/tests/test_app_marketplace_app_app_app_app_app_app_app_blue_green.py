from app.services.app_marketplace_app_app_app_app_app_app_app_blue_green import BlueGreenDeployer

def test_full_cycle():
    bg = BlueGreenDeployer()
    r = bg.deploy_to_inactive("2.0")
    assert r["slot"] == "green"
    bg.mark_healthy("green")
    r2 = bg.switch()
    assert r2["success"]
    assert r2["new_active"] == "green"
    assert bg.status()["active"] == "green"

def test_switch_unhealthy():
    bg = BlueGreenDeployer()
    bg.deploy_to_inactive("2.0")
    r = bg.switch()
    assert not r["success"]
    assert r["reason"] == "inactive_slot_unhealthy"

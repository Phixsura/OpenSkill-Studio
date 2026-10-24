from app.services.app_marketplace_app_app_app_app_app_app_app_blue_green import (
    create_deployment, switch_traffic, deployment_status,
)

def test_switch():
    d = create_deployment("api", "2.0", "2.1")
    assert d["active_slot"] == "blue"
    r = switch_traffic(d, "green")
    assert r["switched"]
    assert r["version"] == "2.1"
    assert d["green"]["traffic_pct"] == 100
    assert d["blue"]["traffic_pct"] == 0

def test_status():
    d = create_deployment("web", "1.0", "1.1")
    s = deployment_status(d)
    assert s["active"]["version"] == "1.0"
    assert s["standby"]["version"] == "1.1"
    assert s["ready_to_switch"]

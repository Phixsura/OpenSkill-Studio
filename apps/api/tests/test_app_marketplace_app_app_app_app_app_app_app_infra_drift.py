from app.services.app_marketplace_app_app_app_app_app_app_app_infra_drift import detect_infra_drift

def test_no_drift():
    r = detect_infra_drift({"vm-1": {"cpu": 4}}, {"vm-1": {"cpu": 4}})
    assert not r["has_drift"]

def test_drift():
    r = detect_infra_drift(
        {"vm-1": {"cpu": 4, "memory": 16}, "vm-2": {"cpu": 2}},
        {"vm-1": {"cpu": 8, "memory": 16}, "vm-3": {"cpu": 2}})
    assert r["has_drift"]
    assert "vm-2" in r["missing"]
    assert "vm-3" in r["extra"]
    assert r["drifted"][0]["resource"] == "vm-1"
    assert r["drifted"][0]["changes"]["cpu"]["desired"] == 4

from app.services.app_marketplace_app_app_app_app_app_app_app_slo_burn import calculate_burn_rate, multi_window

def test_normal():
    r = calculate_burn_rate(10000, 5, 0.999, 1)
    assert r["severity"] == "ok"
    assert r["burn_rate"] < 2

def test_critical():
    r = calculate_burn_rate(1000, 100, 0.999, 1)
    assert r["severity"] == "critical"
    assert r["burn_rate"] > 10

def test_multi_window():
    r = multi_window([
        {"total": 10000, "failed": 5, "hours": 1},
        {"total": 100000, "failed": 50, "hours": 6},
    ], slo_target=0.999)
    assert len(r["windows"]) == 2
    assert not r["alerting"]

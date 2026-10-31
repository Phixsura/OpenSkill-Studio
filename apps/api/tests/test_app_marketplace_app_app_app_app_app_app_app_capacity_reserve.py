from app.services.app_marketplace_app_app_app_app_app_app_app_capacity_reserve import create_reservation, check_utilization

def test_reserve():
    r = create_reservation("prod-api", "cpu", 100, "high")
    assert r["status"] == "active"
    assert r["priority"] == "high"

def test_utilization():
    reservations = [
        {"name": "api", "amount": 100, "utilized": 80},
        {"name": "cache", "amount": 50, "utilized": 10},  # underutilized
    ]
    r = check_utilization(reservations)
    assert r["utilization_pct"] == 60
    assert "cache" in r["underutilized"]
    assert r["waste_count"] == 1

from app.services.app_marketplace_app_app_app_app_app_app_app_dep_sla import calculate_composite_sla, nines_to_downtime

def test_composite():
    r = calculate_composite_sla([
        {"name": "api", "sla_pct": 99.9, "serial": True},
        {"name": "db", "sla_pct": 99.99, "serial": True},
    ])
    assert r["composite_sla"] < 99.9  # serial reduces
    assert r["weakest"] == "api"

def test_downtime():
    r = nines_to_downtime(99.9, 30)
    assert r["downtime_min"] == 43.2
    assert r["nines"] >= 2

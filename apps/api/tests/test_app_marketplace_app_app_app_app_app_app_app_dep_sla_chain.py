from app.services.app_marketplace_app_app_app_app_app_app_app_dep_sla_chain import calculate_chain_sla, weakest_link

def test_chain():
    r = calculate_chain_sla([
        {"name": "gateway", "sla_pct": 99.99},
        {"name": "api", "sla_pct": 99.9},
        {"name": "db", "sla_pct": 99.9},
    ])
    assert r["composite_sla"] < 99.9  # serial reduces
    assert r["services"] == 3
    assert not r["meets_target"]

def test_weakest():
    r = weakest_link([
        {"name": "api", "sla_pct": 99.99},
        {"name": "db", "sla_pct": 99.5},
    ])
    assert r["service"] == "db"
    assert r["sla_pct"] == 99.5

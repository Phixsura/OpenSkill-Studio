from app.services.app_marketplace_app_app_app_app_app_app_app_dep_weight import calculate_weights

def test_weights():
    r = calculate_weights([
        {"name": "api", "depends_on": ["db", "cache"], "request_volume": 50000},
        {"name": "worker", "depends_on": ["db"], "request_volume": 5000},
    ])
    assert r["most_critical"] == "api"
    assert r["weights"]["api"] > r["weights"]["worker"]

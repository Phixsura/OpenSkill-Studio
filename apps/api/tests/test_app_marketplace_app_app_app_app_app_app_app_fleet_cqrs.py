from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cqrs import fleet_cqrs_status
def test_cqrs():
    r = fleet_cqrs_status([{"cqrs_enabled": True, "read_replicas": 3}, {"cqrs_enabled": False}])
    assert r["cqrs_enabled"] == 1
    assert r["read_replicas"] == 3
    assert r["adoption_pct"] == 50.0

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_idempotency import fleet_idempotency
def test_idemp():
    r = fleet_idempotency([{"supports_idempotency": True, "replay_count": 10}, {"supports_idempotency": False}])
    assert r["with_idempotency"] == 1
    assert r["coverage_pct"] == 50.0

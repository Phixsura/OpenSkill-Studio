from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sa_audit import fleet_sa_audit
def test_sa():
    r = fleet_sa_audit([{"last_used_days": 10}, {"last_used_days": 100, "has_long_lived_token": True}])
    assert r["unused"] == 1
    assert r["with_long_tokens"] == 1
    assert not r["clean"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bug_bounty import fleet_bug_bounty
def test_bounty():
    r = fleet_bug_bounty([{"valid": True, "bounty_usd": 5000, "severity": "critical"}, {"valid": False}])
    assert r["valid"] == 1
    assert r["total_paid"] == 5000
    assert r["critical"] == 1

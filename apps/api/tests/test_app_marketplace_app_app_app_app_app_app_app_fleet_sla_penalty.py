from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sla_penalty import fleet_sla_penalty
def test_penalty():
    r = fleet_sla_penalty([{"penalty_usd": 5000, "tier": "enterprise"}, {"penalty_usd": 1000, "tier": "standard"}])
    assert r["total_penalty_usd"] == 6000
    assert not r["clean"]

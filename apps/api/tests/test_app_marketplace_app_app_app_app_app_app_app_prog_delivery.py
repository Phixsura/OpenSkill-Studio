from app.services.app_marketplace_app_app_app_app_app_app_app_prog_delivery import create_progressive_rollout, advance_stage

def test_success():
    r = create_progressive_rollout("api-v3", [
        {"name": "canary", "traffic_pct": 5}, {"name": "partial", "traffic_pct": 50},
        {"name": "full", "traffic_pct": 100}])
    assert r["total_stages"] == 3
    advance_stage(r, True)
    advance_stage(r, True)
    a = advance_stage(r, True)
    assert a["advanced"]
    assert r["status"] == "complete"

def test_rollback():
    r = create_progressive_rollout("api-v3", [{"name": "canary"}, {"name": "full"}])
    advance_stage(r, True)
    a = advance_stage(r, False)
    assert not a["advanced"]
    assert a["action"] == "rollback"
    assert r["status"] == "rolled_back"

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wh_analytics import fleet_webhook_analytics
def test_wh():
    events = [{"event_type": t} for t in ["push", "pr", "issue", "deploy", "release"]]
    r = fleet_webhook_analytics(events)
    assert r["event_types"] == 5
    assert r["diverse"]

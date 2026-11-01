from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_audit_log import fleet_audit_log_stats
def test_audit():
    r = fleet_audit_log_stats([{"type": "login"}, {"type": "login"}, {"type": "deploy"}])
    assert r["total_events"] == 3
    assert r["by_type"]["login"] == 2
    assert r["types"] == 2

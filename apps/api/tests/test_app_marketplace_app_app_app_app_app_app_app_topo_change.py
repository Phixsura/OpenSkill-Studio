from app.services.app_marketplace_app_app_app_app_app_app_app_topo_change import detect_changes

def test_changes():
    r = detect_changes(["api", "db", "cache"], ["api", "db", "queue"],
                          ["api→db", "api→cache"], ["api→db", "api→queue"])
    assert r["services_added"] == ["queue"]
    assert r["services_removed"] == ["cache"]
    assert r["connections_added"] == ["api→queue"]
    assert r["connections_removed"] == ["api→cache"]
    assert r["breaking"]
    assert r["total_changes"] == 4

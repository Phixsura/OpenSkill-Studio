from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grafana import fleet_grafana_dashboards
def test_graf():
    r = fleet_grafana_dashboards([{"views_7d": 50}, {"views_7d": 0, "age_days": 100}, {"views_7d": 10}])
    assert r["active"] == 2
    assert r["stale"] == 1
    assert r["usage_rate"] == 66.7

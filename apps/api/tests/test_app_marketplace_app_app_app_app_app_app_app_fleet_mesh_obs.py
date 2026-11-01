from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mesh_obs import fleet_mesh_observability
def test_obs():
    r = fleet_mesh_observability([
        {"has_traces": True, "has_metrics": True, "has_structured_logs": True},
        {"has_traces": True, "has_metrics": True, "has_structured_logs": False},
    ])
    assert r["full_observability"] == 1
    assert r["coverage_pct"] == 50.0

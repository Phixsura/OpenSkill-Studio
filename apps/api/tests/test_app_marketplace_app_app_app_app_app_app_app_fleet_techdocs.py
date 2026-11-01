from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_techdocs import fleet_techdocs_status
def test_td():
    r = fleet_techdocs_status([{"has_techdocs": True, "build_ok": True}] * 8 + [{"has_techdocs": False}] * 2)
    assert r["coverage_pct"] == 80.0
    assert r["good"]

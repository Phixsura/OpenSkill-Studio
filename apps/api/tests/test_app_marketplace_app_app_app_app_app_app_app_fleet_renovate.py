from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_renovate import fleet_renovate_status
def test_ren():
    r = fleet_renovate_status([{"renovate_enabled": True, "open_prs": 5, "merged_prs_30d": 20}])
    assert r["merged_30d"] == 20
    assert r["active"]

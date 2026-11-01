from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sveltekit import fleet_sveltekit_status
def test_sk():
    r = fleet_sveltekit_status([{"deployed": True, "routes": 80, "ssr_pct": 90}])
    assert r["routes"] == 80
    assert r["all_deployed"]

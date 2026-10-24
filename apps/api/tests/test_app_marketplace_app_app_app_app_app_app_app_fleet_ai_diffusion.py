from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_diffusion import fleet_ai_diffusion
def test_diff():
    r = fleet_ai_diffusion([{"active": True, "generations_24h": 1000000, "avg_steps": 30, "fid": 8.5}])
    assert r["generations_24h"] == 1000000
    assert r["quality"]

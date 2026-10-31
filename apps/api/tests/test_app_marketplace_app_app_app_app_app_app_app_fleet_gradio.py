from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gradio import fleet_gradio_status
def test_gr():
    r = fleet_gradio_status([{"running": True, "interfaces": 5, "users_24h": 10000}])
    assert r["interfaces"] == 5
    assert r["all_running"]

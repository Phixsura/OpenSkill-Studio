from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_streamlit import fleet_streamlit_status
def test_st():
    r = fleet_streamlit_status([{"deployed": True, "viewers_24h": 20000, "components": 50}])
    assert r["viewers_24h"] == 20000
    assert r["all_deployed"]

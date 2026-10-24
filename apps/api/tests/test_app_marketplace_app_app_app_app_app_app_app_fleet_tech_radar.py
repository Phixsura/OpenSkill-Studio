from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tech_radar import fleet_tech_radar
def test_radar():
    r = fleet_tech_radar([{"ring": "adopt"}, {"ring": "trial"}, {"ring": "hold"}, {"ring": "adopt"}])
    assert r["adopt"] == 2
    assert r["hold"] == 1

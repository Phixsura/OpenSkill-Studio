from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_learn_db import fleet_learnings_db
def test_db():
    r = fleet_learnings_db([{"category": "network"}, {"category": "deploy"}, {"category": "network"}])
    assert r["categories"] == 2
    assert r["by_category"]["network"] == 2

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_topic_mod import fleet_ai_topic_modeler
def test_tm():
    r = fleet_ai_topic_modeler([{"active": True, "docs": 10000000, "topics": 500, "coherence": 0.75}])
    assert r["topics"] == 500
    assert r["meaningful"]

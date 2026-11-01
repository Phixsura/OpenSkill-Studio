from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dora_grade import fleet_dora_overall
def test_elite():
    r = fleet_dora_overall("Elite", "Elite", "Elite", "High")
    assert r["overall"] == "Elite"
    assert r["score"] == 3.75

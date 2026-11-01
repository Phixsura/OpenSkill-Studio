from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_priority import fleet_priority_classes
def test_priority():
    r = fleet_priority_classes([{"priority_class": "high"}, {"priority_class": "default"}, {"priority_class": "critical"}])
    assert r["no_priority"] == 1
    assert not r["all_prioritized"]

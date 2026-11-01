from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_resource_tagging_v9 import fleet_resource_tagging_v9
def test_tag_v9():
    r = fleet_resource_tagging_v9([{"tags": {"env": "prod", "team": "platform", "cost-center": "eng"}}])
    assert r["tagged"] == 1
    assert r["compliant"] == 1
    assert r["healthy"]

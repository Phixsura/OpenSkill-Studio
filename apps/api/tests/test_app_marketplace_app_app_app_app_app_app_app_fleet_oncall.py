from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_oncall import fleet_oncall_status
def test_oncall():
    r = fleet_oncall_status([{"on_call": True, "pages_24h": 5}, {"on_call": True, "pages_24h": 15}])
    assert r["active_oncall"] == 2
    assert r["overloaded"] == 1
    assert not r["healthy"]

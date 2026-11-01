from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tf_state import fleet_tf_state
def test_tf():
    r = fleet_tf_state([{"state_locked": False, "last_apply_ok": True}, {"state_locked": True, "last_apply_ok": True}])
    assert r["locked"] == 1
    assert not r["all_ok"]

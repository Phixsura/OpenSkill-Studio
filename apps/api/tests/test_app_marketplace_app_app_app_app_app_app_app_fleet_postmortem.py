from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_postmortem import fleet_postmortem_status
def test_postmortem():
    r = fleet_postmortem_status([{"postmortem_done": True, "actions_completed": True}, {"postmortem_done": False}])
    assert r["postmortems_done"] == 1
    assert r["completion_pct"] == 50.0

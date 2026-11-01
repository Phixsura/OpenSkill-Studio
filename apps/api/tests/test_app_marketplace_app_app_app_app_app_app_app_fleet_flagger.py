from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_flagger import fleet_flagger_status
def test_flagger():
    r = fleet_flagger_status([{"phase": "Succeeded"}, {"phase": "Progressing"}, {"phase": "Failed"}])
    assert r["succeeded"] == 1
    assert r["failed"] == 1
    assert not r["healthy"]

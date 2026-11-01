from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ansible import fleet_ansible_status
def test_ansible():
    r = fleet_ansible_status([{"status": "ok"}, {"status": "changed"}, {"status": "ok"}])
    assert r["ok"] == 2
    assert r["changed"] == 1
    assert not r["idempotent"]

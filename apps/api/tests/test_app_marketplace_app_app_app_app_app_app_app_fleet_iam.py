from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_iam import fleet_iam_status
def test_iam():
    r = fleet_iam_status([{"mfa_enabled": True}, {"mfa_enabled": False, "key_unused_days": 100}])
    assert r["with_mfa"] == 1
    assert r["unused_keys"] == 1
    assert not r["secure"]

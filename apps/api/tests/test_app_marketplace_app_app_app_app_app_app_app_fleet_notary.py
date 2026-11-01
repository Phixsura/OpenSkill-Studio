from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_notary import fleet_notary_status
def test_notary():
    r = fleet_notary_status([{"notary_signed": True, "trust_verified": True}, {"notary_signed": False}])
    assert r["unsigned"] == 1
    assert not r["fully_trusted"]

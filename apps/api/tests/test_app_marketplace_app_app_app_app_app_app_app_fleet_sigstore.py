from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sigstore import fleet_sigstore_status
def test_sig():
    r = fleet_sigstore_status([{"signed": True, "verified": True}, {"signed": True, "verified": True}, {"signed": False}])
    assert r["signed"] == 2
    assert r["unsigned"] == 1
    assert not r["secure"]

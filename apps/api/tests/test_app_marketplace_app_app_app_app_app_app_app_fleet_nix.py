from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nix import fleet_nix_status
def test_nix():
    r = fleet_nix_status([{"uses_nix": True, "reproducible": True}, {"uses_nix": True, "reproducible": False}, {"uses_nix": False}])
    assert r["using_nix"] == 2
    assert r["reproducible"] == 1
    assert r["adoption_pct"] == 66.7

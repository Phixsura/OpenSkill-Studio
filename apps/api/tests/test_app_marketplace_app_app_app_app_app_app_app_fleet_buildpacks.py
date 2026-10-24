from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_buildpacks import fleet_buildpacks_status
def test_bp():
    r = fleet_buildpacks_status([{"uses_buildpacks": True, "build_sec": 120}] * 6 + [{"uses_buildpacks": False}] * 4)
    assert r["using_buildpacks"] == 6
    assert r["modern"]

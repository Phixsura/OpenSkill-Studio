from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_duplication import fleet_code_duplication
def test_dup():
    r = fleet_code_duplication({"duplication_pct": 8, "clone_count": 50})
    assert not r["acceptable"]
    assert not r["needs_refactor"]

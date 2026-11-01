from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_img_vuln import fleet_img_vuln
def test_vuln():
    r = fleet_img_vuln([{"critical": 0, "high": 1}, {"critical": 2, "high": 0}])
    assert r["critical"] == 2
    assert r["high"] == 1
    assert not r["clean"]

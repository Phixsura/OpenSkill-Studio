from app.services.app_marketplace_app_app_app_app_app_app_app_res_quota_enf import enforce
def test_allowed():
    r = enforce("prod", "cpu", 2, 10, 5)
    assert r["allowed"]
    assert r["available"] == 5
def test_denied():
    r = enforce("prod", "cpu", 8, 10, 5)
    assert not r["allowed"]

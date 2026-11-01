from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_window_chk import is_deploy_allowed

def test_allowed():
    r = is_deploy_allowed(14, 1, [{"name": "business_hours", "start_hour": 9, "end_hour": 17, "days": [0,1,2,3,4]}])
    assert r["allowed"]
    assert r["remaining_hours"] == 3

def test_outside():
    r = is_deploy_allowed(22, 1, [{"name": "business_hours", "start_hour": 9, "end_hour": 17}])
    assert not r["allowed"]

def test_freeze():
    r = is_deploy_allowed(14, 1, [{"name": "anytime"}], freeze_active=True)
    assert not r["allowed"]
    assert r["reason"] == "deploy_freeze_active"

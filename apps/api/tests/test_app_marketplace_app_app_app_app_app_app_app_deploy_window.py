from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_window import check_deploy_window, next_available_window

def test_allowed():
    r = check_deploy_window("business_hours", 14, 2)  # Wed 2pm
    assert r["allowed"]

def test_blocked():
    r = check_deploy_window("business_hours", 22, 2)  # Wed 10pm
    assert not r["allowed"]

def test_next():
    r = next_available_window(["business_hours", "off_peak"], 23, 1)  # Tue 11pm
    assert r["available_now"]
    assert r["window"] == "off_peak"

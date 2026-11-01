from app.services.app_marketplace_app_app_app_app_app_app_app_wh_ip_filter import validate_ip_list, check_ip_allowed, get_platform_ips

def test_validate():
    r = validate_ip_list(["10.0.0.0/8", "192.168.1.0/24", "bad!"])
    assert len(r["valid"]) == 2
    assert len(r["invalid"]) == 1
    assert not r["all_valid"]

def test_check():
    r = check_ip_allowed("10.0.1.5", ["10.0.0.0/8", "172.16.0.0/12"])
    assert r["allowed"]
    assert r["matched"] == "10.0.0.0/8"
    r2 = check_ip_allowed("8.8.8.8", ["10.0.0.0/8"])
    assert not r2["allowed"]

def test_platform():
    ips = get_platform_ips()
    assert len(ips) == 3

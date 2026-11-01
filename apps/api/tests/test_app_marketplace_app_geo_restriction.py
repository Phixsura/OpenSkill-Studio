from app.services.app_marketplace_app_geo_restriction import set_geo_policy, check_availability

def test_allow():
    r = set_geo_policy(app_id="a1", mode="allow", countries=["US", "GB", "DE"])
    assert len(r["countries"]) == 3
    assert r["mode"] == "allow"

def test_block():
    r = set_geo_policy(app_id="a1", mode="block", countries=["CN", "RU"])
    assert len(r["countries"]) == 2

def test_invalid_mode():
    r = set_geo_policy(app_id="a1", mode="maybe", countries=["US"])
    assert "error" in r

def test_available():
    r = check_availability(country_code="US", mode="allow", country_list=["US", "GB"])
    assert r["available"]

def test_blocked():
    r = check_availability(country_code="CN", mode="block", country_list=["CN", "RU"])
    assert not r["available"]

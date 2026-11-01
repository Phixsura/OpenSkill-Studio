from app.services.app_marketplace_app_app_app_app_app_app_app_golden_path import define_golden_path, check_against_golden

def test_follows():
    golden = define_golden_path(["gateway", "api", "db"])
    r = check_against_golden(["gateway", "api", "db"], golden["path"])
    assert r["follows_golden"]

def test_deviation():
    r = check_against_golden(["gateway", "cache", "api", "db"], ["gateway", "api", "db"])
    assert not r["follows_golden"]
    assert r["deviations"][0]["expected"] == "api"
    assert r["deviations"][0]["actual"] == "cache"
    assert r["extra_hops"] == ["db"]

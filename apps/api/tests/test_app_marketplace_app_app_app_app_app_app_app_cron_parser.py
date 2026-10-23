from app.services.app_marketplace_app_app_app_app_app_app_app_cron_parser import parse_cron, describe_cron

def test_parse():
    r = parse_cron("30 9 * * 1-5")
    assert r["valid"]
    assert r["fields"]["minute"] == "30"
    assert r["fields"]["hour"] == "9"

def test_preset():
    r = parse_cron("@daily")
    assert r["valid"]
    assert r["is_preset"]
    assert r["expression"] == "0 0 * * *"

def test_describe():
    assert "9:00" in describe_cron("0 9 * * *")
    assert "midnight" in describe_cron("@daily")
    assert "minute" in describe_cron("*/5 * * * *")

def test_invalid():
    r = parse_cron("bad")
    assert not r["valid"]

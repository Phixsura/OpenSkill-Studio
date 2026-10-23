from app.services.app_marketplace_app_app_app_app_app_app_app_tz_converter import convert_hour, team_times, list_timezones

def test_convert():
    r = convert_hour(hour=9, from_tz="PST", to_tz="EST")
    assert r["to_hour"] == 12
    assert r["day_change"] == "same_day"

def test_wrap():
    r = convert_hour(hour=23, from_tz="EST", to_tz="JST")
    assert r["to_hour"] == 13  # 23 + 14 = 37 % 24 = 13
    assert r["day_change"] == "next_day"

def test_team():
    times = team_times(hour=10, from_tz="UTC", team_tzs=["PST", "EST", "JST"])
    assert len(times) == 3
    assert times[0]["to_hour"] == 2  # PST

def test_list():
    tzs = list_timezones()
    assert len(tzs) > 10

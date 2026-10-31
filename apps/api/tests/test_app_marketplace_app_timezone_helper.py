from app.services.app_marketplace_app_timezone_helper import convert_time, get_current_times

def test_convert():
    r = convert_time(utc_time="2026-10-23T12:00:00", target_tz="US/Pacific")
    assert "04:00" in r["converted"]  # 12 - 8 = 4

def test_convert_tokyo():
    r = convert_time(utc_time="2026-10-23T12:00:00", target_tz="Asia/Tokyo")
    assert "21:00" in r["converted"]  # 12 + 9 = 21

def test_invalid_tz():
    r = convert_time(utc_time="2026-10-23T12:00:00", target_tz="Mars/Olympus")
    assert "error" in r

def test_current():
    r = get_current_times(timezones=["UTC", "US/Pacific", "Asia/Tokyo"])
    assert len(r["times"]) == 3

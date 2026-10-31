from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_window import create_window, is_in_window, next_window

def test_create():
    w = create_window("maintenance", day_of_week=6, start_hour=2, duration_hours=4)
    assert w["end_hour"] == 6
    assert w["duration_hours"] == 4

def test_in_window():
    w = create_window("maint", 6, 2, 4)
    r = is_in_window(6, 3, w)
    assert r["in_window"]
    r2 = is_in_window(6, 7, w)
    assert not r2["in_window"]

def test_next():
    windows = [create_window("w1", 3, 2, 2), create_window("w2", 5, 22, 2)]
    r = next_window(windows, current_day=1, current_hour=10)
    assert r["name"] == "w1"
    assert r["hours_until"] == 40  # 2 days - 8 hours

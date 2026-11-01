from app.services.app_marketplace_app_user_journey_map import build_journey_map

def test_journey():
    steps = [
        {"name": "Landing Page", "users": 1000, "avg_time_sec": 15},
        {"name": "Sign Up", "users": 400, "avg_time_sec": 60},
        {"name": "Onboarding", "users": 300, "avg_time_sec": 120},
        {"name": "First Action", "users": 200, "avg_time_sec": 45},
    ]
    r = build_journey_map(steps=steps)
    assert r["overall_conversion"] == 20.0
    assert r["bottleneck"] == "Sign Up"  # 600 drop-off
    assert r["total_steps"] == 4

def test_empty():
    r = build_journey_map(steps=[])
    assert r["total_steps"] == 0
    assert r["overall_conversion"] == 0

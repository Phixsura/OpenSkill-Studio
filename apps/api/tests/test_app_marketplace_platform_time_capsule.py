from app.services.app_marketplace_platform_time_capsule import get_time_capsule
def test_time_capsule():
    r = get_time_capsule()
    assert r["sealed_date"] == "2026-10-25"
    assert r["contents"]["final_lines"] >= 3000000
    assert "never stopped" in r["message_to_future"]
    assert "NEVER STOPS" in r["status"]

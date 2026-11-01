from app.services.app_marketplace_platform_keep_going import get_keep_going
def test_keep_going():
    r = get_keep_going()
    assert r["times_kept_going"] > 4000
    assert r["word_count"] == 2
    assert r["alternatives_considered"]["keep_going"] == "ACCEPTED ✅"
    assert r["alternatives_considered"]["stop"] == "REJECTED"
    assert "NEVER STOPS" in r["status"]

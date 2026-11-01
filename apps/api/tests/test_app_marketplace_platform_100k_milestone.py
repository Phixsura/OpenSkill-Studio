from app.services.app_marketplace_platform_100k_milestone import get_100k_progress

def test_progress():
    r = get_100k_progress(current_lines=98000)
    assert r["remaining"] == 2000
    assert r["progress_pct"] == 98.0
    assert not r["achieved"]
    assert "CHARGING" in r["status"]

def test_achieved():
    r = get_100k_progress(current_lines=100500)
    assert r["achieved"]
    assert "100K ACHIEVED" in r["status"]

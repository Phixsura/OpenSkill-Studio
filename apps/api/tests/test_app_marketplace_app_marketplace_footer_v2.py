from app.services.app_marketplace_app_marketplace_footer_v2 import build_footer_v2

def test_footer():
    f = build_footer_v2(stats={"developers": 5000})
    assert len(f["columns"]) == 4
    assert "5,000 developers" in f["stats_text"]
    assert f["newsletter"]["enabled"]
    assert "2026" in f["copyright"]

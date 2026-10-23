from app.services.app_marketplace_app_app_app_app_app_app_app_app_performance_page import build_performance_page

def test_good():
    r = build_performance_page(metrics={"lcp_ms": 1200, "fid_ms": 50, "cls": 0.05, "ttfb_ms": 200})
    assert r["overall"] == "good"
    assert all(v["score"] == "good" for v in r["vitals"])

def test_poor():
    r = build_performance_page(metrics={"lcp_ms": 5000, "fid_ms": 400, "cls": 0.3, "ttfb_ms": 2000})
    assert r["overall"] == "poor"

from app.services.app_marketplace_app_app_app_app_app_app_app_sli_tracker import create_sli, sli_summary

def test_sli():
    r = create_sli("availability", "http_200", 99950, 100000, 99.9)
    assert r["ratio_pct"] == 99.95
    assert r["meeting_objective"]
    assert r["error_budget_remaining"] > 0

def test_failing():
    r = create_sli("latency", "p99<500ms", 99000, 100000, 99.9)
    assert not r["meeting_objective"]

def test_summary():
    slis = [
        create_sli("a", "m", 9999, 10000, 99.9),
        create_sli("b", "m", 9900, 10000, 99.9),
    ]
    s = sli_summary(slis)
    assert s["meeting"] == 1
    assert not s["all_meeting"]

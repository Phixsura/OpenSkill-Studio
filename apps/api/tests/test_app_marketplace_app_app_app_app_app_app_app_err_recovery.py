from app.services.app_marketplace_app_app_app_app_app_app_app_err_recovery import select_strategy, recovery_report

def test_strategy():
    r = select_strategy("timeout", 1, False)
    assert r["strategy"] == "retry"
    r2 = select_strategy("timeout", 4, True)
    assert r2["strategy"] == "fallback"
    r3 = select_strategy("crash", 15, False)
    assert r3["strategy"] == "rollback"

def test_report():
    events = [{"strategy": "retry"}, {"strategy": "retry"}, {"strategy": "alert"}]
    r = recovery_report(events)
    assert r["auto_recovered"] == 2
    assert r["auto_pct"] == 67

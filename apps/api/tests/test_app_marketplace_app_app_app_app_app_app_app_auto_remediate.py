from app.services.app_marketplace_app_app_app_app_app_app_app_auto_remediate import AutoRemediation

def test_evaluate():
    ar = AutoRemediation()
    ar.add_rule("high_cpu", lambda ctx: ctx.get("cpu_pct", 0) > 90,
                lambda ctx: {"action": "scale_up"}, "critical")
    ar.add_rule("low_disk", lambda ctx: ctx.get("disk_free_pct", 100) < 10,
                lambda ctx: {"action": "cleanup"}, "warning")
    r = ar.evaluate({"cpu_pct": 95, "disk_free_pct": 50})
    assert r["triggered"] == 1
    assert r["actions"][0]["rule"] == "high_cpu"

def test_no_trigger():
    ar = AutoRemediation()
    ar.add_rule("test", lambda ctx: False, lambda ctx: {})
    r = ar.evaluate({})
    assert r["triggered"] == 0

def test_stats():
    ar = AutoRemediation()
    ar.add_rule("r1", lambda _: True, lambda _: {}, "critical")
    ar.evaluate({})
    ar.evaluate({})
    s = ar.stats()
    assert s["actions_taken"] == 2
    assert s["by_severity"]["critical"] == 2

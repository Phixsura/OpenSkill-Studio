from app.services.app_marketplace_crash_reporter import CrashReporter, CrashReport


def test_report_and_group():
    cr = CrashReporter()
    r1 = CrashReport("r1", "ext-1", "2.0.0", "TypeError", "null ref", "at line 42\nat line 10")
    r2 = CrashReport("r2", "ext-1", "2.0.0", "TypeError", "null ref", "at line 42\nat line 10", "org-1")
    g1 = cr.report_crash(r1)
    g2 = cr.report_crash(r2)
    assert g1.fingerprint == g2.fingerprint
    assert g2.count == 2


def test_different_crashes():
    cr = CrashReporter()
    cr.report_crash(CrashReport("r1", "ext-2", "1.0", "TypeError", "a", "stack_a"))
    cr.report_crash(CrashReport("r2", "ext-2", "1.0", "ValueError", "b", "stack_b"))
    top = cr.get_top_crashes("ext-2")
    assert len(top) == 2


def test_crash_free_rate():
    cr = CrashReporter()
    for _ in range(100):
        cr.record_session("ext-3")
    for _ in range(5):
        cr.report_crash(CrashReport("r", "ext-3", "1.0", "Error", "x", "stack"))
    rate = cr.get_crash_free_rate("ext-3")
    assert rate == 95.0


def test_update_status():
    cr = CrashReporter()
    report = CrashReport("r1", "ext-4", "1.0", "Error", "msg", "stack")
    cr.report_crash(report)
    assert cr.update_status("ext-4", report.fingerprint, "resolved") is True
    top = cr.get_top_crashes("ext-4")
    assert top[0].status == "resolved"


def test_summary():
    cr = CrashReporter()
    for _ in range(50):
        cr.record_session("ext-5")
    cr.report_crash(CrashReport("r1", "ext-5", "1.0", "Err", "a", "s1", "o1"))
    cr.report_crash(CrashReport("r2", "ext-5", "2.0", "Err", "b", "s2", "o2"))
    summary = cr.get_summary("ext-5")
    assert summary["total_crashes"] == 2
    assert summary["unique_crashes"] == 2
    assert summary["crash_free_rate"] == 96.0
    assert summary["affected_versions"] == 2

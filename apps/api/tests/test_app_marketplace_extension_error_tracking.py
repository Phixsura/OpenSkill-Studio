from app.services.app_marketplace_extension_error_tracking import ExtErrorTrackingService

def test_report_and_group():
    svc = ExtErrorTrackingService()
    svc.report("ext-1", "TypeError", "undefined is not a function")
    svc.report("ext-1", "TypeError", "undefined is not a function")
    svc.report("ext-1", "RangeError", "Index out of bounds")
    groups = svc.get_groups("ext-1")
    assert len(groups) == 2
    assert groups[0].count == 2  # TypeError grouped

def test_resolve():
    svc = ExtErrorTrackingService()
    svc.report("ext-1", "Error", "Something broke")
    groups = svc.get_groups("ext-1")
    svc.resolve("ext-1", groups[0].fingerprint)
    assert len(svc.get_groups("ext-1")) == 0

def test_error_rate():
    svc = ExtErrorTrackingService()
    svc.report("ext-1", "Error", "A")
    svc.report("ext-1", "Error", "A")
    svc.report("ext-1", "Error", "B")
    assert svc.get_error_rate("ext-1") == 3

from app.services.app_marketplace_extension_api_health_monitor import ApiHealthMonitorService


def test_record_and_health():
    svc = ApiHealthMonitorService()
    svc.configure("/api/users", slo_target=99.0)
    for _ in range(99):
        svc.record("/api/users", True, 50)
    svc.record("/api/users", False, 500)
    h = svc.get_health("/api/users")
    assert h["availability"] == 99.0
    assert h["slo_met"] is True


def test_slo_violation():
    svc = ApiHealthMonitorService()
    svc.configure("/api/data", slo_target=99.9)
    for _ in range(990):
        svc.record("/api/data", True, 30)
    for _ in range(10):
        svc.record("/api/data", False, 1000)
    h = svc.get_health("/api/data")
    assert h["slo_met"] is False


def test_error_budget():
    svc = ApiHealthMonitorService()
    svc.configure("/api/x", slo_target=99.0)
    for _ in range(100):
        svc.record("/api/x", True, 20)
    h = svc.get_health("/api/x")
    assert h["error_budget_remaining"] == 1.0  # 1% of 100 = 1 error allowed


def test_get_violations():
    svc = ApiHealthMonitorService()
    svc.configure("/healthy", slo_target=99.0)
    svc.configure("/broken", slo_target=99.9)
    for _ in range(100):
        svc.record("/healthy", True, 20)
    for _ in range(50):
        svc.record("/broken", True, 20)
    for _ in range(50):
        svc.record("/broken", False, 500)
    violations = svc.get_violations()
    assert len(violations) == 1
    assert violations[0]["endpoint"] == "/broken"

from app.services.app_marketplace_extension_health_checker import HealthCheckerService


def test_record_and_overall():
    svc = HealthCheckerService()
    svc.register("api")
    svc.register("db")
    svc.record("api", "healthy", 5)
    svc.record("db", "healthy", 10)
    result = svc.get_overall()
    assert result["overall"] == "healthy"


def test_down_propagates():
    svc = HealthCheckerService()
    svc.register("api")
    svc.register("db")
    svc.record("api", "healthy")
    svc.record("db", "down", message="Connection refused")
    result = svc.get_overall()
    assert result["overall"] == "down"


def test_dependency_degrades():
    svc = HealthCheckerService()
    svc.register("db")
    svc.register("api", dependencies=["db"])
    svc.record("db", "down")
    svc.record("api", "healthy")
    result = svc.get_overall()
    assert result["components"]["api"] == "degraded"


def test_uptime():
    svc = HealthCheckerService()
    svc.register("api")
    for _ in range(8):
        svc.record("api", "healthy")
    for _ in range(2):
        svc.record("api", "down")
    uptime = svc.get_uptime("api")
    assert uptime == 80.0

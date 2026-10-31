from app.services.app_marketplace_extension_health_aggregator import HealthAggregatorService


def test_healthy_component():
    ha = HealthAggregatorService()
    ha.register("api")
    result = ha.record("api", True, latency_ms=5)
    assert result["healthy"] is True
    assert result["derived_status"] == "healthy"


def test_unhealthy_component():
    ha = HealthAggregatorService()
    ha.register("db")
    result = ha.record("db", False, message="Connection refused")
    assert result["derived_status"] == "down"


def test_dependency_degradation():
    ha = HealthAggregatorService()
    ha.register("db")
    ha.register("api", dependencies=["db"])
    ha.record("db", False)
    ha.record("api", True)
    overall = ha.get_overall()
    assert overall["components"]["api"] == "degraded"
    assert overall["components"]["db"] == "down"
    assert overall["overall"] == "down"


def test_all_healthy():
    ha = HealthAggregatorService()
    ha.register("api")
    ha.register("db")
    ha.register("cache")
    ha.record("api", True)
    ha.record("db", True)
    ha.record("cache", True)
    assert ha.get_overall()["overall"] == "healthy"


def test_uptime():
    ha = HealthAggregatorService()
    ha.register("api")
    for _ in range(8):
        ha.record("api", True)
    for _ in range(2):
        ha.record("api", False)
    uptime = ha.get_uptime("api")
    assert uptime == 80.0


def test_flap_detection():
    ha = HealthAggregatorService()
    ha.register("flaky")
    # Rapid status changes
    for i in range(10):
        ha.record("flaky", i % 2 == 0)
    result = ha.record("flaky", True)
    assert result["flapping"] is True


def test_latency_stats():
    ha = HealthAggregatorService()
    ha.register("api")
    for ms in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        ha.record("api", True, latency_ms=ms)
    stats = ha.get_latency_stats("api")
    assert stats["count"] == 10
    assert stats["avg"] == 55.0
    assert stats["max"] == 100


def test_incidents():
    ha = HealthAggregatorService()
    ha.register("api")
    ha.register("db")
    ha.record("api", True)
    ha.record("db", False, message="Timeout")
    incidents = ha.get_incidents()
    assert len(incidents) == 1
    assert incidents[0]["component"] == "db"
    assert incidents[0]["message"] == "Timeout"


def test_deep_dependency_chain():
    ha = HealthAggregatorService()
    ha.register("storage")
    ha.register("db", dependencies=["storage"])
    ha.register("api", dependencies=["db"])
    ha.record("storage", False)
    ha.record("db", True)
    ha.record("api", True)
    overall = ha.get_overall()
    assert overall["components"]["db"] == "degraded"
    # api depends on db which is degraded (not down), api sees db as healthy
    # but db's dep (storage) is down so db is degraded

from app.services.app_marketplace_app_app_app_app_app_app_app_health_endpoints import HealthEndpointRegistry

def test_register_check():
    her = HealthEndpointRegistry()
    her.register("api", "http://api:8080/health", interval_seconds=15)
    her.record_check("api", 200, 5.0)
    assert her.stats()["healthy"] == 1

def test_unhealthy():
    her = HealthEndpointRegistry()
    her.register("db", "http://db:5432/health")
    for _ in range(3):
        her.record_check("db", 500, 100)
    assert "db" in her.unhealthy_services(min_failures=3)

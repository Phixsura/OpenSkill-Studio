from app.services.app_api_developer_api_circuit_breaker_dashboard import AppAPIDeveloperAPICircuitBreakerDashboard

class TestCircuitBreakerDashboard:
    def test_register(self):
        d = AppAPIDeveloperAPICircuitBreakerDashboard()
        c = d.register("inst-1", "/api/users", failure_threshold=3)
        assert c.state == "closed"

    def test_trip_open(self):
        d = AppAPIDeveloperAPICircuitBreakerDashboard()
        d.register("inst-1", "/api/a", failure_threshold=3)
        for _ in range(3): d.record_failure("inst-1", "/api/a")
        assert d.check_state("inst-1", "/api/a") == "open"

    def test_recovery(self):
        d = AppAPIDeveloperAPICircuitBreakerDashboard()
        d.register("inst-1", "/api/a", failure_threshold=2, recovery_timeout_s=0)
        d.record_failure("inst-1", "/api/a")
        d.record_failure("inst-1", "/api/a")
        assert d.check_state("inst-1", "/api/a") == "half_open"
        d.record_success("inst-1", "/api/a")
        assert d.check_state("inst-1", "/api/a") == "closed"

    def test_open_circuits(self):
        d = AppAPIDeveloperAPICircuitBreakerDashboard()
        d.register("inst-1", "/a", failure_threshold=1)
        d.register("inst-1", "/b", failure_threshold=10)
        d.record_failure("inst-1", "/a")
        assert len(d.open_circuits("inst-1")) == 1

    def test_isolation(self):
        d = AppAPIDeveloperAPICircuitBreakerDashboard()
        d.register("inst-1", "/a")
        assert len(d.all_circuits("inst-2")) == 0

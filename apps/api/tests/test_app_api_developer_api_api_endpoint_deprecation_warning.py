from app.services.app_api_developer_api_api_endpoint_deprecation_warning import AppAPIDeveloperAPIApiEndpointDeprecationWarning

class TestDeprecationWarning:
    def test_register(self):
        w = AppAPIDeveloperAPIApiEndpointDeprecationWarning()
        d = w.register("inst-1", "/api/v1/users", "GET", "/api/v2/users", "2025-06-01")
        assert "Deprecated API" in d.warning_header

    def test_check_returns_warning(self):
        w = AppAPIDeveloperAPIApiEndpointDeprecationWarning()
        w.register("inst-1", "/old", "GET", "/new", "2025-12-31")
        d = w.check("inst-1", "/old", "GET", "consumer-1")
        assert d is not None
        assert d.total_warnings_sent == 1

    def test_check_non_deprecated(self):
        w = AppAPIDeveloperAPIApiEndpointDeprecationWarning()
        assert w.check("inst-1", "/api/v2/users", "GET", "c1") is None

    def test_unique_consumers(self):
        w = AppAPIDeveloperAPIApiEndpointDeprecationWarning()
        w.register("inst-1", "/old", "GET", "/new", "2025-12-31")
        w.check("inst-1", "/old", "GET", "c1")
        w.check("inst-1", "/old", "GET", "c1")
        w.check("inst-1", "/old", "GET", "c2")
        d = w.all_warnings("inst-1")[0]
        assert len(d.consumers_warned) == 2
        assert d.total_warnings_sent == 3

    def test_isolation(self):
        w = AppAPIDeveloperAPIApiEndpointDeprecationWarning()
        w.register("inst-1", "/old", "GET", "/new", "2025-12-31")
        assert len(w.all_warnings("inst-2")) == 0

from app.services.app_api_developer_api_api_rate_limit_sliding_window import AppAPIDeveloperAPIApiRateLimitSlidingWindow

class TestSlidingWindow:
    def test_allow(self):
        w = AppAPIDeveloperAPIApiRateLimitSlidingWindow()
        w.configure("inst-1", "c1", "/api", 60, 100)
        allowed, remaining = w.try_request("inst-1", "c1", "/api")
        assert allowed is True
        assert remaining == 99

    def test_limit(self):
        w = AppAPIDeveloperAPIApiRateLimitSlidingWindow()
        w.configure("inst-1", "c1", "/api", 60, 3)
        for _ in range(3): w.try_request("inst-1", "c1", "/api")
        allowed, remaining = w.try_request("inst-1", "c1", "/api")
        assert allowed is False
        assert remaining == 0

    def test_no_config_allows(self):
        w = AppAPIDeveloperAPIApiRateLimitSlidingWindow()
        allowed, _ = w.try_request("inst-1", "c1", "/api")
        assert allowed is True

    def test_limited_consumers(self):
        w = AppAPIDeveloperAPIApiRateLimitSlidingWindow()
        w.configure("inst-1", "c1", "/api", 60, 1)
        w.configure("inst-1", "c2", "/api", 60, 100)
        w.try_request("inst-1", "c1", "/api")
        assert "c1" in w.limited_consumers("inst-1")
        assert "c2" not in w.limited_consumers("inst-1")

    def test_isolation(self):
        w = AppAPIDeveloperAPIApiRateLimitSlidingWindow()
        w.configure("inst-1", "c1", "/api", 60, 1)
        w.try_request("inst-1", "c1", "/api")
        assert len(w.limited_consumers("inst-2")) == 0

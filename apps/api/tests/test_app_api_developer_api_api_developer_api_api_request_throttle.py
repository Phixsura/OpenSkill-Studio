from app.services.app_api_developer_api_api_developer_api_api_request_throttle import AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle

class TestRequestThrottle:
    def test_configure(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle()
        s = t.configure("inst-1", "c1", 100)
        assert s.current_rate == 100

    def test_backoff(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle()
        t.configure("inst-1", "c1", 100)
        t.apply_backoff("inst-1", "c1")
        s = t.all_states("inst-1")[0]
        assert s.current_rate == 50
        assert s.backoff_factor == 2.0

    def test_max_backoff(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle()
        t.configure("inst-1", "c1", 100)
        for _ in range(10): t.apply_backoff("inst-1", "c1")
        s = t.all_states("inst-1")[0]
        assert s.backoff_factor == 16.0
        assert s.current_rate >= 1

    def test_reset(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle()
        t.configure("inst-1", "c1", 100)
        t.apply_backoff("inst-1", "c1")
        t.reset_backoff("inst-1", "c1")
        s = t.all_states("inst-1")[0]
        assert s.current_rate == 100

    def test_throttled_consumers(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle()
        t.configure("inst-1", "c1", 100)
        t.configure("inst-1", "c2", 50)
        t.apply_backoff("inst-1", "c1")
        assert len(t.throttled_consumers("inst-1")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle()
        t.configure("inst-1", "c1", 100)
        assert len(t.all_states("inst-2")) == 0

from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_consumer_authentication_tracker import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker

class TestConsumerAuthTracker:
    def test_record_success(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker()
        r = t.record_auth("inst-1", "c1", "api_key", True)
        assert r.successful == 1
        assert r.failure_rate == 0.0

    def test_record_failure(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker()
        r = t.record_auth("inst-1", "c1", "jwt", False, "expired token")
        assert r.failed == 1
        assert r.last_failure_reason == "expired token"

    def test_high_failure_rate(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker()
        for _ in range(9): t.record_auth("inst-1", "c1", "api_key", True)
        for _ in range(3): t.record_auth("inst-1", "c1", "api_key", False)
        assert len(t.high_failure_rate("inst-1", 20)) == 1

    def test_by_method(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker()
        t.record_auth("inst-1", "c1", "api_key", True)
        t.record_auth("inst-1", "c2", "oauth2", True)
        assert t.by_method("inst-1") == {"api_key": 1, "oauth2": 1}

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTracker()
        t.record_auth("inst-1", "c1", "api_key", True)
        assert len(t.all_records("inst-2")) == 0

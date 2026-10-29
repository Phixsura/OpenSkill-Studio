from app.services.app_api_developer_api_api_developer_api_rate_limit_token_bucket import AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket

class TestTokenBucket:
    def test_configure(self):
        t = AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket()
        b = t.configure("inst-1", "c1", "/api", 100, 10.0)
        assert b.tokens == 100.0

    def test_consume(self):
        t = AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket()
        t.configure("inst-1", "c1", "/api", 10, 1.0)
        allowed, remaining = t.try_consume("inst-1", "c1", "/api", 5)
        assert allowed is True
        assert remaining == 5.0

    def test_exhausted(self):
        t = AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket()
        t.configure("inst-1", "c1", "/api", 3, 0.1)
        for _ in range(3): t.try_consume("inst-1", "c1", "/api")
        allowed, _ = t.try_consume("inst-1", "c1", "/api")
        assert allowed is False

    def test_no_config_allows(self):
        t = AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket()
        allowed, _ = t.try_consume("inst-1", "c1", "/api")
        assert allowed is True

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket()
        t.configure("inst-1", "c1", "/api", 10, 1.0)
        assert len(t.all_buckets("inst-2")) == 0

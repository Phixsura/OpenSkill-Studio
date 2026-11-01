from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_rate_limit_token_bucket import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucket

class TestTokenBucket:
    def test_consume_within_capacity(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucket()
        svc.configure("inst-1", "c1", "/api", capacity=10, refill_rate=1.0)
        result = svc.try_consume("inst-1", "c1", "/api", 5)
        assert result["allowed"] is True

    def test_exceed_capacity(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucket()
        svc.configure("inst-1", "c1", "/api", capacity=5, refill_rate=1.0)
        svc.try_consume("inst-1", "c1", "/api", 5)
        result = svc.try_consume("inst-1", "c1", "/api", 1)
        assert result["allowed"] is False
        assert "retry_after_s" in result

    def test_no_bucket_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucket()
        result = svc.try_consume("inst-1", "c1", "/api")
        assert result["allowed"] is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucket()
        svc.configure("inst-1", "c1", "/api", capacity=10, refill_rate=1.0)
        assert len(svc.list_buckets("inst-2")) == 0

from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_correlation_id import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId

class TestRequestCorrelationId:
    def test_generate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId()
        entry = svc.generate("inst-1", "c1", "GET", "/users")
        assert entry.correlation_id.startswith("cor-")

    def test_complete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId()
        entry = svc.generate("inst-1", "c1", "GET", "/api")
        svc.complete("inst-1", entry.correlation_id, 200, 50.0)
        e = svc.lookup("inst-1", entry.correlation_id)
        assert e.status_code == 200 and e.duration_ms == 50.0

    def test_chain(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId()
        parent = svc.generate("inst-1", "c1", "GET", "/api")
        child = svc.generate("inst-1", "c1", "GET", "/db", parent_id=parent.correlation_id)
        chain = svc.get_chain("inst-1", child.correlation_id)
        assert len(chain) == 2 and chain[0].correlation_id == parent.correlation_id

    def test_unique_ids(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId()
        e1 = svc.generate("inst-1", "c1", "GET", "/a")
        e2 = svc.generate("inst-1", "c1", "GET", "/a")
        assert e1.correlation_id != e2.correlation_id

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId()
        svc.generate("inst-1", "c1", "GET", "/a")
        assert svc.entry_count("inst-2") == 0

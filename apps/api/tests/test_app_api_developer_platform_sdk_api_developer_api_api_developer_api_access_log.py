from app.services.app_api_developer_platform_sdk_api_developer_api_api_developer_api_access_log import AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog

class TestAccessLog:
    def test_record(self):
        l = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog()
        e = l.record("inst-1", "e1", "c1", "GET", "/api/users", 200, 45)
        assert e.method == "GET"

    def test_search_by_consumer(self):
        l = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog()
        l.record("inst-1", "e1", "c1", "GET", "/api", 200, 30)
        l.record("inst-1", "e2", "c2", "GET", "/api", 200, 40)
        assert len(l.search("inst-1", consumer_id="c1")) == 1

    def test_search_errors(self):
        l = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog()
        l.record("inst-1", "e1", "c1", "GET", "/a", 200, 30)
        l.record("inst-1", "e2", "c1", "GET", "/b", 500, 100)
        assert len(l.search("inst-1", min_status=400)) == 1

    def test_error_count(self):
        l = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog()
        l.record("inst-1", "e1", "c1", "GET", "/a", 200, 30)
        l.record("inst-1", "e2", "c1", "GET", "/b", 500, 100)
        l.record("inst-1", "e3", "c1", "GET", "/c", 404, 20)
        assert l.error_count("inst-1") == 2

    def test_isolation(self):
        l = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLog()
        l.record("inst-1", "e1", "c1", "GET", "/api", 200, 30)
        assert l.total("inst-2") == 0

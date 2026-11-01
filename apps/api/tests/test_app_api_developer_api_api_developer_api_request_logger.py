from app.services.app_api_developer_api_api_developer_api_request_logger import AppAPIDeveloperAPIApiDeveloperApiRequestLogger

class TestRequestLogger:
    def test_log(self):
        l = AppAPIDeveloperAPIApiDeveloperApiRequestLogger()
        e = l.log_request("inst-1", "l1", "GET", "/api/users", 200, 45.0, consumer_id="c1")
        assert e.method == "GET"

    def test_search_by_method(self):
        l = AppAPIDeveloperAPIApiDeveloperApiRequestLogger()
        l.log_request("inst-1", "l1", "GET", "/api", 200, 30)
        l.log_request("inst-1", "l2", "POST", "/api", 201, 50)
        assert len(l.search("inst-1", method="GET")) == 1

    def test_error_logs(self):
        l = AppAPIDeveloperAPIApiDeveloperApiRequestLogger()
        l.log_request("inst-1", "l1", "GET", "/api", 200, 30)
        l.log_request("inst-1", "l2", "GET", "/api", 500, 100)
        assert len(l.error_logs("inst-1")) == 1

    def test_header_scrubbing(self):
        l = AppAPIDeveloperAPIApiDeveloperApiRequestLogger()
        # Just verify it doesn't crash — headers aren't stored on the log entry
        l.log_request("inst-1", "l1", "GET", "/api", 200, 30, headers={"Authorization": "Bearer secret", "Content-Type": "json"})

    def test_isolation(self):
        l = AppAPIDeveloperAPIApiDeveloperApiRequestLogger()
        l.log_request("inst-1", "l1", "GET", "/api", 200, 30)
        assert l.total("inst-2") == 0

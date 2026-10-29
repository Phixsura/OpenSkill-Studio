from app.services.app_api_developer_api_api_error_classification import AppAPIDeveloperAPIApiErrorClassification

class TestErrorClassification:
    def test_classify_auth(self):
        c = AppAPIDeveloperAPIApiErrorClassification()
        b = c.classify("inst-1", 401, "UNAUTHORIZED", "/api/users", "Invalid token")
        assert b.category == "auth"

    def test_classify_rate_limit(self):
        c = AppAPIDeveloperAPIApiErrorClassification()
        b = c.classify("inst-1", 429, "RATE_LIMITED", "/api/data")
        assert b.category == "rate_limit"

    def test_classify_server(self):
        c = AppAPIDeveloperAPIApiErrorClassification()
        b = c.classify("inst-1", 500, "INTERNAL_ERROR", "/api/process")
        assert b.category == "server"

    def test_accumulate(self):
        c = AppAPIDeveloperAPIApiErrorClassification()
        c.classify("inst-1", 400, "INVALID_INPUT", "/api/a")
        c.classify("inst-1", 400, "INVALID_INPUT", "/api/b")
        top = c.top_errors("inst-1")
        assert top[0].count == 2
        assert len(top[0].endpoints_affected) == 2

    def test_by_category(self):
        c = AppAPIDeveloperAPIApiErrorClassification()
        c.classify("inst-1", 401, "AUTH", "/a")
        c.classify("inst-1", 500, "ERR", "/b")
        cats = c.by_category("inst-1")
        assert cats["auth"] == 1
        assert cats["server"] == 1

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiErrorClassification()
        c.classify("inst-1", 500, "ERR", "/a")
        assert c.total_errors("inst-2") == 0

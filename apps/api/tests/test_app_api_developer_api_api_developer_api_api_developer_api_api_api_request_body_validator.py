from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_request_body_validator import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator

class TestRequestBodyValidator:
    def test_required(self):
        v = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator()
        v.add_rule("inst-1", "/api/users", "name", "required", "")
        r = v.validate("inst-1", "/api/users", {})
        assert not r.valid
        assert any("required" in e for e in r.errors)

    def test_max_length(self):
        v = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator()
        v.add_rule("inst-1", "/api", "name", "max_length", "5")
        r = v.validate("inst-1", "/api", {"name": "toolong"})
        assert not r.valid

    def test_min_max_value(self):
        v = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator()
        v.add_rule("inst-1", "/api", "age", "min_value", "0")
        v.add_rule("inst-1", "/api", "age", "max_value", "150")
        assert v.validate("inst-1", "/api", {"age": 25}).valid is True
        assert v.validate("inst-1", "/api", {"age": -1}).valid is False

    def test_valid(self):
        v = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator()
        v.add_rule("inst-1", "/api", "name", "required", "")
        r = v.validate("inst-1", "/api", {"name": "Alice"})
        assert r.valid is True

    def test_stats(self):
        v = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidator()
        v.add_rule("inst-1", "/api", "name", "required", "")
        v.validate("inst-1", "/api", {"name": "ok"})
        v.validate("inst-1", "/api", {})
        s = v.stats("inst-1")
        assert s["total"] == 2
        assert s["invalid"] == 1

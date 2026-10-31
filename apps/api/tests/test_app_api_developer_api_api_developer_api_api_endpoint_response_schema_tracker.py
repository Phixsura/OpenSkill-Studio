from app.services.app_api_developer_api_api_developer_api_api_endpoint_response_schema_tracker import AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker

class TestResponseSchemaTracker:
    def test_no_drift(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker()
        t.register("inst-1", "/api/users", "GET", ["id", "name", "email"])
        s = t.check("inst-1", "/api/users", "GET", ["id", "name", "email"])
        assert s.has_drift is False

    def test_missing_field(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker()
        t.register("inst-1", "/api/users", "GET", ["id", "name", "email"])
        s = t.check("inst-1", "/api/users", "GET", ["id", "name"])
        assert s.has_drift is True
        assert "email" in s.missing_fields

    def test_extra_field(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker()
        t.register("inst-1", "/api/users", "GET", ["id", "name"])
        s = t.check("inst-1", "/api/users", "GET", ["id", "name", "avatar"])
        assert "avatar" in s.extra_fields

    def test_drifted_list(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker()
        t.register("inst-1", "/a", "GET", ["id"])
        t.register("inst-1", "/b", "GET", ["id"])
        t.check("inst-1", "/a", "GET", ["id", "extra"])
        t.check("inst-1", "/b", "GET", ["id"])
        assert len(t.drifted("inst-1")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker()
        t.register("inst-1", "/api", "GET", ["id"])
        assert len(t.all_schemas("inst-2")) == 0

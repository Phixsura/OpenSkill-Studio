from app.services.app_api_developer_api_api_developer_api_api_api_documentation_generator import AppAPIDeveloperAPIApiDeveloperApiApiApiDocumentationGenerator

class TestDocumentationGenerator:
    def test_create_and_add(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiApiDocumentationGenerator()
        g.create("inst-1", "My API", "2.0")
        g.add_endpoint("inst-1", "GET", "/api/users", "List users", tags=["users"])
        doc = g.get("inst-1")
        assert doc.endpoint_count == 1

    def test_documented_pct(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiApiDocumentationGenerator()
        g.create("inst-1", "API", "1.0")
        g.add_endpoint("inst-1", "GET", "/a", "A", examples=[{"status": 200}])
        g.add_endpoint("inst-1", "POST", "/b", "B")
        assert g.get("inst-1").documented_pct == 50.0

    def test_render_markdown(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiApiDocumentationGenerator()
        g.create("inst-1", "Test API", "1.0")
        g.add_endpoint("inst-1", "GET", "/users", "Get users", parameters=[{"name": "limit", "type": "int", "description": "Max results"}])
        md = g.render_markdown("inst-1")
        assert "# Test API" in md
        assert "GET /users" in md
        assert "`limit`" in md

    def test_isolation(self):
        g = AppAPIDeveloperAPIApiDeveloperApiApiApiDocumentationGenerator()
        g.create("inst-1", "API", "1.0")
        assert g.get("inst-2") is None

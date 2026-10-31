from app.services.app_api_endpoint_documentation import AppAPIEndpointDocumentation

class TestDoc:
    def test_document(self):
        d = AppAPIEndpointDocumentation()
        doc = d.document("inst-1", "GET", "/api/users", "List users", parameters=["limit", "offset"])
        assert len(doc.parameters) == 2

    def test_get(self):
        d = AppAPIEndpointDocumentation()
        d.document("inst-1", "GET", "/api/users", "List users")
        assert d.get_doc("inst-1", "GET", "/api/users") is not None
        assert d.get_doc("inst-1", "POST", "/api/users") is None

    def test_undocumented(self):
        d = AppAPIEndpointDocumentation()
        d.document("inst-1", "GET", "/api/users", "List")
        undoc = d.undocumented("inst-1", [("GET", "/api/users"), ("POST", "/api/users")])
        assert undoc == [("POST", "/api/users")]

    def test_isolation(self):
        d = AppAPIEndpointDocumentation()
        d.document("inst-1", "GET", "/api", "Summary")
        assert d.list_docs("inst-2") == []

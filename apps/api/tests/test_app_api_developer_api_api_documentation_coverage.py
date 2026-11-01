from app.services.app_api_developer_api_api_documentation_coverage import AppAPIDeveloperAPIApiDocumentationCoverage

class TestDocCoverage:
    def test_fully_documented(self):
        c = AppAPIDeveloperAPIApiDocumentationCoverage()
        d = c.register("inst-1", "/api/users", "GET", True, True, True, True)
        assert d.fully_documented is True
        assert d.coverage_score == 4

    def test_partial(self):
        c = AppAPIDeveloperAPIApiDocumentationCoverage()
        d = c.register("inst-1", "/api/users", "GET", True, False, True, False)
        assert d.coverage_score == 2
        assert d.fully_documented is False

    def test_coverage_pct(self):
        c = AppAPIDeveloperAPIApiDocumentationCoverage()
        c.register("inst-1", "/a", "GET", True, True, True, True)  # 4/4
        c.register("inst-1", "/b", "GET", True, False, False, False)  # 1/4
        assert c.coverage_pct("inst-1") == 62.5

    def test_undocumented(self):
        c = AppAPIDeveloperAPIApiDocumentationCoverage()
        c.register("inst-1", "/a", "GET", True, True, True, True)
        c.register("inst-1", "/b", "POST", True, False, False, False)
        assert len(c.undocumented("inst-1")) == 1

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiDocumentationCoverage()
        c.register("inst-1", "/a", "GET", True, True, True, True)
        assert c.coverage_pct("inst-2") == 0.0

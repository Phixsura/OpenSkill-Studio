from app.services.app_api_developer_api_api_developer_api_api_developer_portal_search import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch

class TestPortalSearch:
    def test_index_and_search(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch()
        s.index("inst-1", "r1", "GET /api/users", "Retrieve all users", "endpoint", "/docs/users")
        results = s.search("inst-1", "users")
        assert len(results) == 1
        assert results[0].relevance_score > 0

    def test_title_ranks_higher(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch()
        s.index("inst-1", "r1", "Authentication Guide", "How to use tokens", "guide", "/docs/auth")
        s.index("inst-1", "r2", "Rate Limits", "Authentication is important for rate limits", "documentation", "/docs/rates")
        results = s.search("inst-1", "Authentication")
        assert results[0].result_id == "r1"

    def test_filter_by_type(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch()
        s.index("inst-1", "r1", "Users endpoint", "Get users", "endpoint", "/api/users")
        s.index("inst-1", "r2", "Users guide", "How to use", "guide", "/docs/users")
        results = s.search("inst-1", "Users", result_type="endpoint")
        assert len(results) == 1

    def test_empty_query(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch()
        assert s.search("inst-1", "") == []

    def test_query_count(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch()
        s.search("inst-1", "test")
        s.search("inst-1", "another")
        assert s.query_count("inst-1") == 2

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch()
        s.index("inst-1", "r1", "Test", "Content", "guide", "/test")
        assert s.total_indexed("inst-2") == 0

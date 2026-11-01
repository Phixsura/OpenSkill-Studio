from app.services.app_api_developer_api_graphql_query_analyzer import AppAPIDeveloperAPIGraphQLQueryAnalyzer

class TestGraphQLQueryAnalyzer:
    def test_simple_query(self):
        a = AppAPIDeveloperAPIGraphQLQueryAnalyzer()
        r = a.analyze("inst-1", "q1", "{ user { name email } }")
        assert r.depth == 2
        assert not r.has_introspection

    def test_deep_query_warning(self):
        a = AppAPIDeveloperAPIGraphQLQueryAnalyzer(max_depth=2)
        q = "{ a { b { c { d } } } }"
        r = a.analyze("inst-1", "q1", q)
        assert r.depth == 4
        assert any("Depth" in w for w in r.warnings)

    def test_introspection_detection(self):
        a = AppAPIDeveloperAPIGraphQLQueryAnalyzer()
        r = a.analyze("inst-1", "q1", "{ __schema { types { name } } }")
        assert r.has_introspection is True

    def test_expensive_queries(self):
        a = AppAPIDeveloperAPIGraphQLQueryAnalyzer(max_cost=10)
        a.analyze("inst-1", "q1", "{ a { b { c { d { e { f } } } } } }")
        assert len(a.expensive_queries("inst-1", threshold=10)) >= 1

    def test_isolation(self):
        a = AppAPIDeveloperAPIGraphQLQueryAnalyzer()
        a.analyze("inst-1", "q1", "{ user { name } }")
        assert len(a.recent("inst-2")) == 0

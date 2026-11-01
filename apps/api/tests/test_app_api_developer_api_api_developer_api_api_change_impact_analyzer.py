from app.services.app_api_developer_api_api_developer_api_api_change_impact_analyzer import AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer

class TestChangeImpactAnalyzer:
    def test_low_risk(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer()
        r = a.assess("inst-1", "c1", "/api/users", "field_added", ["c1"])
        assert r.risk_level == "low"

    def test_critical_removal(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer()
        r = a.assess("inst-1", "c1", "/api/old", "endpoint_removed", ["c1", "c2", "c3"], breaking=True)
        assert r.risk_level == "critical"
        assert r.breaking is True

    def test_impact_score(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer()
        r = a.assess("inst-1", "c1", "/api", "field_removed", ["c1", "c2", "c3", "c4", "c5"], breaking=True)
        assert r.impact_score >= 90

    def test_high_risk_filter(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer()
        a.assess("inst-1", "c1", "/a", "field_added", [])
        a.assess("inst-1", "c2", "/b", "endpoint_removed", ["c1"], breaking=True)
        assert len(a.high_risk("inst-1")) == 1

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer()
        a.assess("inst-1", "c1", "/api", "field_added", [])
        assert len(a.all_assessments("inst-2")) == 0

import pytest
from app.services.app_api_developer_api_api_endpoint_scoring import AppAPIDeveloperAPIApiEndpointScoring

class TestEndpointScoring:
    def test_score_a(self):
        s = AppAPIDeveloperAPIApiEndpointScoring()
        r = s.score("inst-1", "/api/users", 99, 95, 98, 90)
        assert r.grade == "A"
        assert r.composite_score > 90

    def test_score_f(self):
        s = AppAPIDeveloperAPIApiEndpointScoring()
        r = s.score("inst-1", "/api/legacy", 40, 30, 20, 10)
        assert r.grade == "F"

    def test_invalid_score(self):
        s = AppAPIDeveloperAPIApiEndpointScoring()
        with pytest.raises(ValueError):
            s.score("inst-1", "/api", 110, 50, 50, 50)

    def test_ranked(self):
        s = AppAPIDeveloperAPIApiEndpointScoring()
        s.score("inst-1", "/fast", 99, 99, 99, 99)
        s.score("inst-1", "/slow", 50, 50, 50, 50)
        ranked = s.ranked("inst-1")
        assert ranked[0].endpoint == "/fast"

    def test_failing(self):
        s = AppAPIDeveloperAPIApiEndpointScoring()
        s.score("inst-1", "/good", 95, 90, 90, 85)
        s.score("inst-1", "/bad", 40, 30, 20, 10)
        assert len(s.failing("inst-1")) == 1

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiEndpointScoring()
        s.score("inst-1", "/api", 90, 90, 90, 90)
        assert len(s.ranked("inst-2")) == 0

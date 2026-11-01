import pytest
from app.services.app_api_developer_api_api_dependency_graph import AppAPIDeveloperAPIApiDependencyGraph

class TestDependencyGraph:
    def test_add_service(self):
        g = AppAPIDeveloperAPIApiDependencyGraph()
        g.add_service("inst-1", "db", "Database")
        n = g.add_service("inst-1", "api", "API Server", ["db"])
        assert n.dependencies == ["db"]

    def test_dependents_updated(self):
        g = AppAPIDeveloperAPIApiDependencyGraph()
        g.add_service("inst-1", "db", "Database")
        g.add_service("inst-1", "api", "API", ["db"])
        db = g.all_services("inst-1")[0]
        assert "api" in db.dependents

    def test_impact_analysis(self):
        g = AppAPIDeveloperAPIApiDependencyGraph()
        g.add_service("inst-1", "db", "Database")
        g.add_service("inst-1", "api", "API", ["db"])
        g.add_service("inst-1", "web", "Web", ["api"])
        affected = g.impact_analysis("inst-1", "db")
        assert len(affected) == 2

    def test_health(self):
        g = AppAPIDeveloperAPIApiDependencyGraph()
        g.add_service("inst-1", "db", "DB")
        g.set_health("inst-1", "db", "down")
        assert g.all_services("inst-1")[0].health == "down"

    def test_isolation(self):
        g = AppAPIDeveloperAPIApiDependencyGraph()
        g.add_service("inst-1", "db", "DB")
        assert len(g.all_services("inst-2")) == 0

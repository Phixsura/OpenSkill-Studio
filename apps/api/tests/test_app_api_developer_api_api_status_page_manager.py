import pytest
from app.services.app_api_developer_api_api_status_page_manager import AppAPIDeveloperAPIApiStatusPageManager

class TestStatusPageManager:
    def test_add_component(self):
        m = AppAPIDeveloperAPIApiStatusPageManager()
        c = m.add_component("inst-1", "api", "API Server")
        assert c.status == "operational"

    def test_update_status(self):
        m = AppAPIDeveloperAPIApiStatusPageManager()
        m.add_component("inst-1", "api", "API Server")
        c = m.update_component("inst-1", "api", "degraded")
        assert c.status == "degraded"

    def test_overall_operational(self):
        m = AppAPIDeveloperAPIApiStatusPageManager()
        m.add_component("inst-1", "api", "API")
        m.add_component("inst-1", "db", "Database")
        assert m.overall_status("inst-1") == "operational"

    def test_overall_major_outage(self):
        m = AppAPIDeveloperAPIApiStatusPageManager()
        m.add_component("inst-1", "api", "API")
        m.update_component("inst-1", "api", "major_outage")
        assert m.overall_status("inst-1") == "major_outage"

    def test_create_incident(self):
        m = AppAPIDeveloperAPIApiStatusPageManager()
        i = m.create_incident("inst-1", "inc-1", "API Down", "critical", "Investigating")
        assert i.status == "investigating"

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiStatusPageManager()
        m.add_component("inst-1", "api", "API")
        assert len(m.all_components("inst-2")) == 0

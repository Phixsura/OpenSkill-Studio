import pytest
from app.services.app_api_developer_api_integration_hub import AppAPIDeveloperAPIIntegrationHub

class TestHub:
    def test_connect(self):
        h = AppAPIDeveloperAPIIntegrationHub()
        i = h.connect("inst-1", "i1", "Slack Alerts", "slack")
        assert i.status == "connected"

    def test_disconnect(self):
        h = AppAPIDeveloperAPIIntegrationHub()
        h.connect("inst-1", "i1", "Slack", "slack")
        h.disconnect("inst-1", "i1")
        assert h.connected("inst-1") == []

    def test_events(self):
        h = AppAPIDeveloperAPIIntegrationHub()
        h.connect("inst-1", "i1", "Slack", "slack")
        h.record_event("inst-1", "i1")
        assert h.list_integrations("inst-1")[0].event_count == 1

    def test_isolation(self):
        h = AppAPIDeveloperAPIIntegrationHub()
        h.connect("inst-1", "i1", "Slack", "slack")
        assert h.list_integrations("inst-2") == []

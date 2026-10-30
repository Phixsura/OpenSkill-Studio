import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_status_page import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage, ServiceComponent,
)

class TestConsumerApiStatusPage:
    def test_all_operational(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        svc.add_component("inst-1", ServiceComponent(component_id="db", name="Database"))
        summary = svc.get_summary("inst-1")
        assert summary.overall_status == "operational" and len(summary.components) == 2

    def test_degraded_overall(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        svc.add_component("inst-1", ServiceComponent(component_id="db", name="Database", status="degraded"))
        summary = svc.get_summary("inst-1")
        assert summary.overall_status == "degraded"

    def test_major_outage_wins(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API", status="degraded"))
        svc.add_component("inst-1", ServiceComponent(component_id="db", name="DB", status="major_outage"))
        summary = svc.get_summary("inst-1")
        assert summary.overall_status == "major_outage"

    def test_update_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        svc.update_status("inst-1", "api", "partial_outage")
        assert svc.list_components("inst-1")[0].status == "partial_outage"

    def test_empty_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage()
        summary = svc.get_summary("inst-1")
        assert summary.overall_status == "operational"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        assert len(svc.list_components("inst-2")) == 0

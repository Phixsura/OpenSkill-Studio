from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_status_page import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage, ServiceComponent, ServiceStatus, Incident,
)

class TestApiStatusPage:
    def test_all_operational(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        svc.add_component("inst-1", ServiceComponent(component_id="db", name="Database"))
        assert svc.overall_status("inst-1") == ServiceStatus.OPERATIONAL

    def test_degraded_propagates(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        svc.update_status("inst-1", "api", ServiceStatus.DEGRADED)
        assert svc.overall_status("inst-1") == ServiceStatus.DEGRADED

    def test_major_outage_wins(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API", status=ServiceStatus.DEGRADED))
        svc.add_component("inst-1", ServiceComponent(component_id="db", name="DB", status=ServiceStatus.MAJOR_OUTAGE))
        assert svc.overall_status("inst-1") == ServiceStatus.MAJOR_OUTAGE

    def test_incidents(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage()
        svc.create_incident("inst-1", Incident(incident_id="i1", title="DB slow", status="investigating", impact=ServiceStatus.DEGRADED))
        assert len(svc.active_incidents("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage()
        svc.add_component("inst-1", ServiceComponent(component_id="api", name="API"))
        assert len(svc.list_components("inst-2")) == 0

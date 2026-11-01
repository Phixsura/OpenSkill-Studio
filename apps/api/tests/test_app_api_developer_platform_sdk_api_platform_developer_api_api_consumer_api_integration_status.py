from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_integration_status import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatus, IntegrationCheck, IntegrationPhase,
)

CHECKS = [IntegrationCheck("c1", "API key created", required=True), IntegrationCheck("c2", "First request", required=True), IntegrationCheck("c3", "Webhook configured", required=False)]

class TestIntegrationStatus:
    def test_create(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatus()
        s = svc.create_status("inst-1", "consumer-1", [IntegrationCheck("c1", "Key", required=True)])
        assert s.phase == IntegrationPhase.NOT_STARTED
        assert s.completion_pct == 0.0

    def test_pass_checks_to_production(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatus()
        svc.create_status("inst-1", "c1", [IntegrationCheck("c1", "Key", required=True), IntegrationCheck("c2", "Request", required=True)])
        svc.pass_check("inst-1", "c1", "c1")
        svc.pass_check("inst-1", "c1", "c2")
        s = svc.get_status("inst-1", "c1")
        assert s.ready_for_production is True
        assert s.phase == IntegrationPhase.PRODUCTION

    def test_not_ready_without_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatus()
        svc.create_status("inst-1", "c1", [IntegrationCheck("c1", "Key", required=True), IntegrationCheck("c2", "Optional", required=False)])
        svc.pass_check("inst-1", "c1", "c2")
        assert svc.get_status("inst-1", "c1").ready_for_production is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatus()
        svc.create_status("inst-1", "c1", [IntegrationCheck("c1", "X", required=True)])
        assert len(svc.list_statuses("inst-2")) == 0

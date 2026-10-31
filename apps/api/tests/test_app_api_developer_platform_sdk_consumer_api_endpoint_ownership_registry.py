import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_ownership_registry import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry, EndpointOwner,
)

class TestEndpointOwnershipRegistry:
    def test_register_and_get(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry()
        svc.register("inst-1", EndpointOwner(endpoint_path="/api/users", team="backend", owner_email="alice@co.com"))
        owner = svc.get_owner("inst-1", "/api/users")
        assert owner.team == "backend" and owner.owner_email == "alice@co.com"

    def test_find_by_team(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry()
        svc.register("inst-1", EndpointOwner(endpoint_path="/api/users", team="backend", owner_email="a@co.com"))
        svc.register("inst-1", EndpointOwner(endpoint_path="/api/orders", team="backend", owner_email="b@co.com"))
        svc.register("inst-1", EndpointOwner(endpoint_path="/api/billing", team="payments", owner_email="c@co.com"))
        assert len(svc.find_by_team("inst-1", "backend")) == 2

    def test_report_with_unowned(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry()
        svc.register("inst-1", EndpointOwner(endpoint_path="/api/users", team="backend", owner_email="a@co.com"))
        report = svc.get_report("inst-1", all_endpoints=["/api/users", "/api/orders", "/api/billing"])
        assert len(report.unowned) == 2 and "/api/orders" in report.unowned

    def test_transfer(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry()
        svc.register("inst-1", EndpointOwner(endpoint_path="/api/users", team="old-team", owner_email="old@co.com"))
        svc.transfer("inst-1", "/api/users", "new-team", "new@co.com")
        assert svc.get_owner("inst-1", "/api/users").team == "new-team"

    def test_team_required(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry()
        with pytest.raises(ValueError, match="team is required"):
            svc.register("inst-1", EndpointOwner(endpoint_path="/api", team="", owner_email="x"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointOwnershipRegistry()
        svc.register("inst-1", EndpointOwner(endpoint_path="/api", team="x", owner_email="y"))
        assert svc.get_owner("inst-2", "/api") is None

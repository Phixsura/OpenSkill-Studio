import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_dependency_injection import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection, ServiceBinding,
)

class TestConsumerApiDependencyInjection:
    def test_bind_and_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection()
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b1", interface_name="IPaymentService", implementation="StripePayment"))
        result = svc.resolve("inst-1", "c1", "IPaymentService")
        assert result.resolved and result.implementation == "StripePayment"

    def test_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection()
        result = svc.resolve("inst-1", "c1", "IMissing")
        assert not result.resolved

    def test_override(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection()
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b1", interface_name="ICache", implementation="Redis"))
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b2", interface_name="ICache", implementation="Memcached"))
        assert svc.resolve("inst-1", "c1", "ICache").implementation == "Memcached"

    def test_unbind(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection()
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b1", interface_name="ICache", implementation="Redis"))
        svc.unbind("inst-1", "c1", "ICache")
        assert not svc.resolve("inst-1", "c1", "ICache").resolved

    def test_resolve_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection()
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b1", interface_name="ICache", implementation="Redis"))
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b2", interface_name="IDB", implementation="Postgres"))
        all_bindings = svc.resolve_all("inst-1", "c1")
        assert len(all_bindings) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjection()
        svc.bind("inst-1", "c1", ServiceBinding(binding_id="b1", interface_name="ICache", implementation="Redis"))
        assert not svc.resolve("inst-2", "c1", "ICache").resolved

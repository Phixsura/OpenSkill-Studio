import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_lifecycle import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle, LifecycleState,
)

class TestConsumerLifecycle:
    def test_register(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle()
        cl = svc.register("inst-1", "c1")
        assert cl.state == LifecycleState.REGISTERED

    def test_valid_transitions(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle()
        svc.register("inst-1", "c1")
        svc.transition("inst-1", "c1", LifecycleState.ONBOARDING)
        svc.transition("inst-1", "c1", LifecycleState.ACTIVE)
        cl = svc._get("inst-1", "c1")
        assert cl.state == LifecycleState.ACTIVE and cl.transition_count == 2

    def test_invalid_transition(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle()
        svc.register("inst-1", "c1")
        with pytest.raises(ValueError, match="Cannot transition"):
            svc.transition("inst-1", "c1", LifecycleState.ACTIVE)  # skip onboarding

    def test_by_state(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle()
        svc.register("inst-1", "c1")
        svc.register("inst-1", "c2")
        svc.transition("inst-1", "c1", LifecycleState.ONBOARDING)
        states = svc.consumers_by_state("inst-1")
        assert states["registered"] == 1 and states["onboarding"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle()
        svc.register("inst-1", "c1")
        assert len(svc.list_consumers("inst-2")) == 0

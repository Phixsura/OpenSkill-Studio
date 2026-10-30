import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_sla_tier import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier, SLATier, SLAAssignment,
)

class TestConsumerSlaTier:
    def test_define_and_assign(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier()
        svc.define_tier("inst-1", SLATier(tier_id="gold", name="Gold", uptime_pct=99.9, max_latency_ms=200, max_error_rate_pct=0.1, priority=2))
        svc.assign("inst-1", SLAAssignment(consumer_id="c1", tier_id="gold", effective_from="2026-01-01"))
        tier = svc.get_tier("inst-1", "c1")
        assert tier.name == "Gold"

    def test_compliance_pass(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier()
        svc.define_tier("inst-1", SLATier(tier_id="gold", name="Gold", uptime_pct=99.9, max_latency_ms=200, max_error_rate_pct=0.1))
        svc.assign("inst-1", SLAAssignment(consumer_id="c1", tier_id="gold", effective_from="2026-01-01"))
        result = svc.check_compliance("inst-1", "c1", actual_uptime=99.95, actual_latency_ms=150, actual_error_rate=0.05)
        assert result.overall_compliant

    def test_compliance_fail(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier()
        svc.define_tier("inst-1", SLATier(tier_id="gold", name="Gold", uptime_pct=99.9, max_latency_ms=200, max_error_rate_pct=0.1))
        svc.assign("inst-1", SLAAssignment(consumer_id="c1", tier_id="gold", effective_from="2026-01-01"))
        result = svc.check_compliance("inst-1", "c1", actual_uptime=99.5, actual_latency_ms=300, actual_error_rate=0.5)
        assert not result.overall_compliant and not result.uptime_compliant

    def test_unassigned(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier()
        assert svc.get_tier("inst-1", "c1") is None

    def test_list_tiers_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier()
        svc.define_tier("inst-1", SLATier(tier_id="silver", name="Silver", uptime_pct=99.5, max_latency_ms=500, max_error_rate_pct=1.0, priority=1))
        svc.define_tier("inst-1", SLATier(tier_id="gold", name="Gold", uptime_pct=99.9, max_latency_ms=200, max_error_rate_pct=0.1, priority=2))
        tiers = svc.list_tiers("inst-1")
        assert tiers[0].name == "Gold"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier()
        svc.define_tier("inst-1", SLATier(tier_id="gold", name="Gold", uptime_pct=99.9, max_latency_ms=200, max_error_rate_pct=0.1))
        assert len(svc.list_tiers("inst-2")) == 0

import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_credit_system import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem,
)

class TestConsumerApiCreditSystem:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_add_and_balance(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem()
        svc.add_credits("inst-1", "c1", 1000, "Purchase", self._now())
        bal = svc.get_balance("inst-1", "c1")
        assert bal.balance == 1000 and bal.total_purchased == 1000

    def test_consume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem()
        svc.add_credits("inst-1", "c1", 100, "Top-up", self._now())
        svc.consume("inst-1", "c1", 30, "API call", self._now())
        bal = svc.get_balance("inst-1", "c1")
        assert bal.balance == 70 and bal.total_consumed == 30

    def test_insufficient(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem()
        svc.add_credits("inst-1", "c1", 10, "Top-up", self._now())
        with pytest.raises(ValueError, match="Insufficient"):
            svc.consume("inst-1", "c1", 20, "Over-spend", self._now())

    def test_transactions(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem()
        svc.add_credits("inst-1", "c1", 100, "Buy", self._now())
        svc.consume("inst-1", "c1", 25, "Use", self._now())
        txs = svc.get_transactions("inst-1", "c1")
        assert len(txs) == 2 and txs[0].amount == 100 and txs[1].amount == -25

    def test_negative_add_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem()
        with pytest.raises(ValueError, match="positive"):
            svc.add_credits("inst-1", "c1", -5, "hack", self._now())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem()
        svc.add_credits("inst-1", "c1", 100, "x", self._now())
        assert svc.get_balance("inst-2", "c1").balance == 0

import pytest
from app.services.app_api_developer_api_api_developer_api_api_consumer_billing_profile import AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile

class TestConsumerBillingProfile:
    def test_create(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        p = b.create("inst-1", "c1", "pro", "billing@acme.com", monthly_budget_cents=100000)
        assert p.plan == "pro"

    def test_invalid_email(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        with pytest.raises(ValueError):
            b.create("inst-1", "c1", "free", "not-email")

    def test_add_charge(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        b.create("inst-1", "c1", "pro", "a@b.com", monthly_budget_cents=10000)
        b.add_charge("inst-1", "c1", 5000)
        assert b._get("inst-1", "c1").budget_usage_pct == 50.0

    def test_over_budget(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        b.create("inst-1", "c1", "starter", "a@b.com", monthly_budget_cents=1000)
        b.add_charge("inst-1", "c1", 1500)
        assert len(b.over_budget_consumers("inst-1")) == 1

    def test_upgrade_only(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        b.create("inst-1", "c1", "pro", "a@b.com")
        with pytest.raises(ValueError, match="upgrade"):
            b.upgrade_plan("inst-1", "c1", "starter")

    def test_isolation(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        b.create("inst-1", "c1", "free", "a@b.com")
        assert b.by_plan("inst-2") == {}

    def test_duplicate_rejected(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerBillingProfile()
        b.create("inst-1", "c1", "free", "a@b.com")
        with pytest.raises(ValueError, match="already exists"):
            b.create("inst-1", "c1", "pro", "new@b.com")

import pytest
from app.services.app_api_developer_api_api_quota_allocation import AppAPIDeveloperAPIApiQuotaAllocation

class TestQuotaAllocation:
    def test_allocate_and_consume(self):
        q = AppAPIDeveloperAPIApiQuotaAllocation()
        q.allocate("inst-1", "c1", "daily", 1000)
        r = q.consume("inst-1", "c1", "daily", 100)
        assert r.remaining == 900
        assert r.usage_pct == 10.0

    def test_exhausted(self):
        q = AppAPIDeveloperAPIApiQuotaAllocation()
        q.allocate("inst-1", "c1", "daily", 10)
        q.consume("inst-1", "c1", "daily", 10)
        with pytest.raises(ValueError, match="exhausted"):
            q.consume("inst-1", "c1", "daily", 1)

    def test_exhausted_consumers(self):
        q = AppAPIDeveloperAPIApiQuotaAllocation()
        q.allocate("inst-1", "c1", "daily", 10)
        q.allocate("inst-1", "c2", "daily", 100)
        q.consume("inst-1", "c1", "daily", 10)
        assert len(q.exhausted_consumers("inst-1")) == 1

    def test_reset(self):
        q = AppAPIDeveloperAPIApiQuotaAllocation()
        q.allocate("inst-1", "c1", "daily", 100)
        q.consume("inst-1", "c1", "daily", 50)
        q.reset("inst-1", "c1", "daily")
        assert q.check("inst-1", "c1", "daily").used == 0

    def test_isolation(self):
        q = AppAPIDeveloperAPIApiQuotaAllocation()
        q.allocate("inst-1", "c1", "daily", 100)
        assert len(q.exhausted_consumers("inst-2")) == 0

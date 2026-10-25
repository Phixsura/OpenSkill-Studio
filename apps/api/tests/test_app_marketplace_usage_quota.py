from app.services.app_marketplace_usage_quota import (
    UsageQuotaManager, QuotaType, OveragePolicy,
)


def test_set_and_consume():
    qm = UsageQuotaManager()
    qm.set_quota("org-1", QuotaType.API_CALLS, 100)
    ok, _ = qm.consume("org-1", QuotaType.API_CALLS, 50)
    assert ok is True
    quota = qm.get_quota("org-1", QuotaType.API_CALLS)
    assert quota.used == 50
    assert quota.remaining == 50


def test_block_on_exceed():
    qm = UsageQuotaManager()
    qm.set_quota("org-2", QuotaType.STORAGE_MB, 10)
    qm.consume("org-2", QuotaType.STORAGE_MB, 8)
    ok, msg = qm.consume("org-2", QuotaType.STORAGE_MB, 5)
    assert ok is False
    assert "exceeded" in msg


def test_throttle_policy():
    qm = UsageQuotaManager()
    qm.set_quota("org-3", QuotaType.API_CALLS, 10, OveragePolicy.THROTTLE)
    qm.consume("org-3", QuotaType.API_CALLS, 10)
    ok, msg = qm.consume("org-3", QuotaType.API_CALLS, 5)
    assert ok is True
    assert "Throttled" in msg


def test_alert_threshold():
    qm = UsageQuotaManager()
    qm.set_quota("org-4", QuotaType.WEBHOOKS, 100, alert_threshold=0.8)
    qm.consume("org-4", QuotaType.WEBHOOKS, 85)
    alerts = qm.get_alerts("org-4")
    assert len(alerts) == 1
    assert "85" in str(alerts[0]["usage_percent"])


def test_get_all_quotas():
    qm = UsageQuotaManager()
    qm.set_quota("org-5", QuotaType.API_CALLS, 1000)
    qm.set_quota("org-5", QuotaType.STORAGE_MB, 500)
    qm.consume("org-5", QuotaType.API_CALLS, 200)
    all_q = qm.get_all_quotas("org-5")
    assert len(all_q) == 2
    api = next(q for q in all_q if q["type"] == "api_calls")
    assert api["used"] == 200
    assert api["remaining"] == 800


def test_reset():
    qm = UsageQuotaManager()
    qm.set_quota("org-6", QuotaType.COMPUTE_SECONDS, 3600)
    qm.consume("org-6", QuotaType.COMPUTE_SECONDS, 1000)
    qm.reset_quota("org-6", QuotaType.COMPUTE_SECONDS)
    quota = qm.get_quota("org-6", QuotaType.COMPUTE_SECONDS)
    assert quota.used == 0

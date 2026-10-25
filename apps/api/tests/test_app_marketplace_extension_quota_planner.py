from app.services.app_marketplace_extension_quota_planner import (
    QuotaPlanner, QuotaTier, UsageSnapshot,
)


def test_recommend_free():
    qp = QuotaPlanner()
    qp.record_usage("org-1", UsageSnapshot(500, 50, 5, 2))
    rec = qp.recommend_tier("org-1")
    assert rec["recommended"] == "free"


def test_recommend_starter():
    qp = QuotaPlanner()
    qp.record_usage("org-2", UsageSnapshot(5000, 500, 30, 10))
    rec = qp.recommend_tier("org-2")
    assert rec["recommended"] == "starter"


def test_recommend_professional():
    qp = QuotaPlanner()
    qp.record_usage("org-3", UsageSnapshot(50000, 5000, 200, 50))
    rec = qp.recommend_tier("org-3")
    assert rec["recommended"] == "professional"


def test_predict_overage():
    qp = QuotaPlanner()
    qp.assign_tier("org-4", QuotaTier.FREE)
    qp.record_usage("org-4", UsageSnapshot(900, 90, 8, 4))  # near free limits
    prediction = qp.predict_overage("org-4")
    assert prediction["at_risk"] is True
    assert prediction["metrics"]["api_calls"]["pct"] == 90.0


def test_no_risk():
    qp = QuotaPlanner()
    qp.assign_tier("org-5", QuotaTier.ENTERPRISE)
    qp.record_usage("org-5", UsageSnapshot(1000, 100, 10, 5))
    prediction = qp.predict_overage("org-5")
    assert prediction["at_risk"] is False


def test_savings():
    qp = QuotaPlanner()
    qp.assign_tier("org-6", QuotaTier.PROFESSIONAL)
    qp.record_usage("org-6", UsageSnapshot(500, 50, 5, 2))  # only needs free
    savings = qp.get_savings("org-6")
    assert savings is not None
    assert savings["recommended"] == "free"
    assert savings["monthly_savings_cents"] == 4999


def test_no_savings():
    qp = QuotaPlanner()
    qp.assign_tier("org-7", QuotaTier.FREE)
    qp.record_usage("org-7", UsageSnapshot(500, 50, 5, 2))
    assert qp.get_savings("org-7") is None

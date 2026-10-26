from app.services.app_marketplace_extension_revenue_analytics import (
    RevenueAnalyticsService, TransactionType,
)
import pytest


def test_record_and_mrr():
    svc = RevenueAnalyticsService()
    svc.record("ext-1", "dev-1", 2999, TransactionType.SUBSCRIPTION, tier="pro")
    svc.record("ext-1", "dev-1", 999, TransactionType.SUBSCRIPTION, tier="basic")
    assert svc.get_mrr("ext-1") == 3998


def test_total_revenue():
    svc = RevenueAnalyticsService()
    svc.record("ext-1", "dev-1", 5000, TransactionType.ONE_TIME)
    svc.record("ext-1", "dev-1", -1000, TransactionType.REFUND)
    result = svc.get_total_revenue("ext-1")
    assert result["net_cents"] == 4000
    assert result["platform_fee_cents"] == 600  # 15%
    assert result["developer_cents"] == 3400


def test_revenue_by_tier():
    svc = RevenueAnalyticsService()
    svc.record("ext-1", "dev-1", 999, TransactionType.SUBSCRIPTION, tier="basic")
    svc.record("ext-1", "dev-1", 2999, TransactionType.SUBSCRIPTION, tier="pro")
    svc.record("ext-1", "dev-1", 2999, TransactionType.SUBSCRIPTION, tier="pro")
    by_tier = svc.get_revenue_by_tier("ext-1")
    assert by_tier["basic"] == 999
    assert by_tier["pro"] == 5998


def test_developer_earnings():
    svc = RevenueAnalyticsService()
    svc.record("ext-1", "dev-1", 10000, TransactionType.SUBSCRIPTION)
    svc.record("ext-1", "dev-1", -2000, TransactionType.REFUND)
    result = svc.get_developer_earnings("dev-1")
    assert result["gross_cents"] == 10000
    assert result["refunds_cents"] == 2000
    assert result["owed_cents"] == 6800  # (10000-2000)*0.85


def test_negative_non_refund_rejected():
    svc = RevenueAnalyticsService()
    with pytest.raises(ValueError, match="refunds"):
        svc.record("ext-1", "dev-1", -500, TransactionType.SUBSCRIPTION)


def test_top_extensions():
    svc = RevenueAnalyticsService()
    svc.record("ext-a", "dev-1", 1000, TransactionType.ONE_TIME)
    svc.record("ext-b", "dev-2", 5000, TransactionType.SUBSCRIPTION)
    svc.record("ext-c", "dev-3", 3000, TransactionType.ONE_TIME)
    top = svc.get_top_extensions(2)
    assert len(top) == 2
    assert top[0]["extension_id"] == "ext-b"

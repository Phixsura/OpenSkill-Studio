from app.services.app_marketplace_extension_developer_payout import (
    DeveloperPayoutService, PaymentMethod, PayoutStatus,
)
import pytest


def test_configure_and_add_earnings():
    svc = DeveloperPayoutService()
    svc.configure("dev-1", PaymentMethod.STRIPE)
    bal = svc.add_earnings("dev-1", 10000)  # $100
    assert bal == 8500  # 85% after 15% fee


def test_request_payout():
    svc = DeveloperPayoutService()
    svc.configure("dev-1", PaymentMethod.PAYPAL, tax_rate=0.1)
    svc.add_earnings("dev-1", 10000)
    payout = svc.request_payout("dev-1")
    assert isinstance(payout, object)
    assert payout.gross_cents == 8500
    assert payout.tax_cents == 850
    assert payout.net_cents == 7650
    assert svc.get_balance("dev-1") == 0


def test_below_threshold():
    svc = DeveloperPayoutService()
    svc.configure("dev-1", PaymentMethod.STRIPE, min_threshold_cents=5000)
    svc.add_earnings("dev-1", 1000)  # Only $8.50 after fee
    result = svc.request_payout("dev-1")
    assert isinstance(result, dict)
    assert "below minimum" in result["error"]


def test_no_config():
    svc = DeveloperPayoutService()
    result = svc.request_payout("dev-1")
    assert "error" in result


def test_complete_payout():
    svc = DeveloperPayoutService()
    svc.configure("dev-1", PaymentMethod.BANK_TRANSFER)
    svc.add_earnings("dev-1", 100000)
    payout = svc.request_payout("dev-1")
    assert svc.complete_payout(payout.payout_id, "ref-123") is True
    assert payout.status == PayoutStatus.COMPLETED


def test_failed_payout_refunds():
    svc = DeveloperPayoutService()
    svc.configure("dev-1", PaymentMethod.STRIPE)
    svc.add_earnings("dev-1", 100000)
    payout = svc.request_payout("dev-1")
    original_gross = payout.gross_cents
    assert svc.fail_payout(payout.payout_id) is True
    assert svc.get_balance("dev-1") == original_gross


def test_invalid_tax_rate():
    svc = DeveloperPayoutService()
    with pytest.raises(ValueError, match="0-50%"):
        svc.configure("dev-1", PaymentMethod.STRIPE, tax_rate=0.8)

from app.services.app_marketplace_extension_revenue_share import ExtRevenueShareService

def test_record_sale():
    svc = ExtRevenueShareService()
    tx = svc.record_sale("ext-1", "dev-1", 1000)  # $10.00
    assert tx.net_cents == 850  # 15% fee
    assert tx.platform_fee_pct == 15.0

def test_custom_fee():
    svc = ExtRevenueShareService()
    svc.set_fee("dev-1", 10.0)
    tx = svc.record_sale("ext-1", "dev-1", 1000)
    assert tx.net_cents == 900  # 10% fee

def test_developer_earnings():
    svc = ExtRevenueShareService()
    svc.record_sale("ext-1", "dev-1", 1000)
    svc.record_sale("ext-2", "dev-1", 2000)
    earnings = svc.get_developer_earnings("dev-1")
    assert earnings["total_gross"] == 3000
    assert earnings["transaction_count"] == 2

def test_platform_revenue():
    svc = ExtRevenueShareService()
    svc.record_sale("ext-1", "dev-1", 1000)
    rev = svc.get_platform_revenue()
    assert rev["total_fees"] == 150
    assert rev["total_payouts"] == 850

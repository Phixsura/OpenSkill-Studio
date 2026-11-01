from app.services.app_marketplace_extension_billing_portal import BillingPortalService

def test_create_and_pay():
    svc = BillingPortalService()
    inv = svc.create_invoice("dev-1", 4999, "Pro plan - October")
    assert svc.pay_invoice(inv.invoice_id) is True
    assert inv.status == "paid"

def test_subscribe_and_cancel():
    svc = BillingPortalService()
    sub = svc.subscribe("dev-1", "pro")
    assert sub.status == "active"
    svc.cancel_subscription("dev-1")
    assert svc.get_subscription("dev-1").status == "cancelled"

def test_revenue():
    svc = BillingPortalService()
    inv1 = svc.create_invoice("dev-1", 4999)
    inv2 = svc.create_invoice("dev-2", 999)
    svc.pay_invoice(inv1.invoice_id)
    svc.pay_invoice(inv2.invoice_id)
    assert svc.get_total_revenue() == 5998

def test_invoices():
    svc = BillingPortalService()
    svc.create_invoice("dev-1", 100)
    svc.create_invoice("dev-1", 200)
    svc.create_invoice("dev-2", 300)
    assert len(svc.get_invoices("dev-1")) == 2

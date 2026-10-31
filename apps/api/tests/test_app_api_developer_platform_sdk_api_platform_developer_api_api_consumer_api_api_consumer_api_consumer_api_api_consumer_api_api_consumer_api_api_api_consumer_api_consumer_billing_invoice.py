import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_consumer_billing_invoice import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice, Invoice, InvoiceLineItem,
)

class TestConsumerBillingInvoice:
    def _now(self):
        return datetime(2026, 6, 1)

    def _invoice(self, iid="inv1"):
        return Invoice(invoice_id=iid, consumer_id="c1", period="2026-06", line_items=[
            InvoiceLineItem(description="API Calls", quantity=10000, unit_price_cents=1, total_cents=10000),
            InvoiceLineItem(description="Bandwidth", quantity=50, unit_price_cents=100, total_cents=5000),
        ], tax_cents=1500)

    def test_create_and_totals(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice()
        inv = svc.create("inst-1", self._invoice())
        assert inv.subtotal_cents == 15000 and inv.total_cents == 16500

    def test_lifecycle(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice()
        svc.create("inst-1", self._invoice())
        svc.issue("inst-1", "inv1", self._now())
        svc.mark_paid("inst-1", "inv1", self._now())
        inv = svc.list_invoices("inst-1", "c1", status="paid")
        assert len(inv) == 1 and inv[0].paid_at is not None

    def test_void(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice()
        svc.create("inst-1", self._invoice())
        svc.void("inst-1", "inv1")
        assert svc.list_invoices("inst-1", "c1")[0].status == "void"

    def test_cannot_void_paid(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice()
        svc.create("inst-1", self._invoice())
        svc.issue("inst-1", "inv1", self._now())
        svc.mark_paid("inst-1", "inv1", self._now())
        with pytest.raises(ValueError, match="Cannot void"):
            svc.void("inst-1", "inv1")

    def test_revenue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice()
        svc.create("inst-1", self._invoice("inv1"))
        svc.issue("inst-1", "inv1", self._now())
        svc.mark_paid("inst-1", "inv1", self._now())
        assert svc.get_total_revenue("inst-1") == 16500

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice()
        svc.create("inst-1", self._invoice())
        assert len(svc.list_invoices("inst-2", "c1")) == 0

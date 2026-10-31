import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_billing_invoice import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice, Invoice, LineItem, InvoiceStatus,
)

class TestConsumerBillingInvoice:
    def test_create_and_total(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice()
        inv = svc.create_invoice("inst-1", Invoice(invoice_id="inv-1", consumer_id="c1", period="2024-01", line_items=[LineItem("API calls", 10000, 1), LineItem("Storage", 5, 500)]))
        assert inv.total_cents == 12500
        assert inv.total_dollars == "$125.00"

    def test_issue_and_pay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice()
        svc.create_invoice("inst-1", Invoice(invoice_id="inv-1", consumer_id="c1", period="2024-01", line_items=[LineItem("API", 100, 10)]))
        svc.issue("inst-1", "inv-1")
        inv = svc.mark_paid("inst-1", "inv-1")
        assert inv.status == InvoiceStatus.PAID

    def test_cannot_void_paid(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice()
        svc.create_invoice("inst-1", Invoice(invoice_id="inv-1", consumer_id="c1", period="2024-01", line_items=[LineItem("X", 1, 100)]))
        svc.issue("inst-1", "inv-1")
        svc.mark_paid("inst-1", "inv-1")
        with pytest.raises(ValueError, match="Cannot void paid"):
            svc.void("inst-1", "inv-1")

    def test_outstanding(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice()
        svc.create_invoice("inst-1", Invoice(invoice_id="inv-1", consumer_id="c1", period="2024-01", line_items=[LineItem("X", 1, 100)]))
        svc.issue("inst-1", "inv-1")
        assert len(svc.outstanding("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice()
        svc.create_invoice("inst-1", Invoice(invoice_id="inv-1", consumer_id="c1", period="2024-01", line_items=[LineItem("X", 1, 100)]))
        assert len(svc.list_invoices("inst-2")) == 0

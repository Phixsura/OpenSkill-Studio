"""Tests for App Org Billing — invoices, payments, balance."""

import pytest

from app.services.app_org_billing import AppOrgBilling, InvoiceStatus

ITEMS = [
    {"description": "API Calls (10K)", "quantity": 10, "unit_price_cents": 100},
    {"description": "Storage (1GB)", "quantity": 1, "unit_price_cents": 500},
]


class TestCreateInvoice:
    def test_create(self):
        b = AppOrgBilling()
        inv = b.create_invoice("inst-1", "inv-1", ITEMS, due_date="2026-11-28")
        assert inv.invoice_id == "inv-1"
        assert inv.status == InvoiceStatus.DRAFT
        assert inv.total_cents == 1500  # 10*100 + 1*500

    def test_total_dollars(self):
        b = AppOrgBilling()
        inv = b.create_invoice("inst-1", "inv-1", ITEMS)
        assert inv.total_dollars == 15.0

    def test_empty_items(self):
        b = AppOrgBilling()
        with pytest.raises(ValueError, match="at least one"):
            b.create_invoice("inst-1", "inv-1", [])

    def test_duplicate(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        with pytest.raises(ValueError, match="already exists"):
            b.create_invoice("inst-1", "inv-1", ITEMS)


class TestLifecycle:
    def test_send(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        inv = b.send_invoice("inst-1", "inv-1")
        assert inv.status == InvoiceStatus.SENT

    def test_pay(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        b.send_invoice("inst-1", "inv-1")
        inv = b.pay_invoice("inst-1", "inv-1")
        assert inv.status == InvoiceStatus.PAID

    def test_cannot_pay_draft(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        with pytest.raises(ValueError, match="Cannot pay"):
            b.pay_invoice("inst-1", "inv-1")

    def test_void(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        inv = b.void_invoice("inst-1", "inv-1")
        assert inv.status == InvoiceStatus.VOID

    def test_cannot_void_paid(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        b.send_invoice("inst-1", "inv-1")
        b.pay_invoice("inst-1", "inv-1")
        with pytest.raises(ValueError, match="Cannot void"):
            b.void_invoice("inst-1", "inv-1")


class TestBalance:
    def test_outstanding(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        b.send_invoice("inst-1", "inv-1")
        b.create_invoice("inst-1", "inv-2", ITEMS)
        b.send_invoice("inst-1", "inv-2")
        assert b.outstanding_balance_cents("inst-1") == 3000

    def test_paid_not_outstanding(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        b.send_invoice("inst-1", "inv-1")
        b.pay_invoice("inst-1", "inv-1")
        assert b.outstanding_balance_cents("inst-1") == 0


class TestListInvoices:
    def test_filter_by_status(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        b.create_invoice("inst-1", "inv-2", ITEMS)
        b.send_invoice("inst-1", "inv-1")
        sent = b.list_invoices("inst-1", status=InvoiceStatus.SENT)
        assert len(sent) == 1


class TestIsolation:
    def test_cross_installation(self):
        b = AppOrgBilling()
        b.create_invoice("inst-1", "inv-1", ITEMS)
        with pytest.raises(KeyError):
            b.get_invoice("inst-2", "inv-1")

"""Consumer API Consumer Billing Invoice — generate and manage invoices."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class InvoiceLineItem:
    description: str
    quantity: int
    unit_price_cents: int
    total_cents: int

@dataclass
class Invoice:
    invoice_id: str
    consumer_id: str
    period: str
    line_items: list[InvoiceLineItem] = field(default_factory=list)
    subtotal_cents: int = 0
    tax_cents: int = 0
    total_cents: int = 0
    status: str = "draft"  # "draft", "issued", "paid", "overdue", "void"
    issued_at: datetime | None = None
    paid_at: datetime | None = None
    due_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerBillingInvoice:
    def __init__(self) -> None:
        self._invoices: dict[tuple[str, str], Invoice] = {}

    def create(self, installation_id: str, invoice: Invoice) -> Invoice:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not invoice.line_items:
            raise ValueError("Invoice must have at least one line item")
        key = (installation_id, invoice.invoice_id)
        if key in self._invoices:
            raise ValueError(f"Invoice {invoice.invoice_id} already exists")
        invoice.subtotal_cents = sum(li.total_cents for li in invoice.line_items)
        invoice.total_cents = invoice.subtotal_cents + invoice.tax_cents
        invoice.status = "draft"
        self._invoices[key] = invoice
        return invoice

    def issue(self, installation_id: str, invoice_id: str, now: datetime) -> Invoice:
        key = (installation_id, invoice_id)
        inv = self._invoices.get(key)
        if not inv:
            raise ValueError("Invoice not found")
        if inv.status != "draft":
            raise ValueError("Only draft invoices can be issued")
        inv.status = "issued"
        inv.issued_at = now
        return inv

    def mark_paid(self, installation_id: str, invoice_id: str, now: datetime) -> Invoice:
        key = (installation_id, invoice_id)
        inv = self._invoices.get(key)
        if not inv:
            raise ValueError("Invoice not found")
        if inv.status not in ("issued", "overdue"):
            raise ValueError("Only issued/overdue invoices can be paid")
        inv.status = "paid"
        inv.paid_at = now
        return inv

    def void(self, installation_id: str, invoice_id: str) -> Invoice:
        key = (installation_id, invoice_id)
        inv = self._invoices.get(key)
        if not inv:
            raise ValueError("Invoice not found")
        if inv.status == "paid":
            raise ValueError("Cannot void a paid invoice")
        inv.status = "void"
        return inv

    def list_invoices(self, installation_id: str, consumer_id: str, status: str | None = None) -> list[Invoice]:
        invoices = [i for (inst, _), i in self._invoices.items() if inst == installation_id and i.consumer_id == consumer_id]
        if status:
            invoices = [i for i in invoices if i.status == status]
        return sorted(invoices, key=lambda i: i.period, reverse=True)

    def get_total_revenue(self, installation_id: str) -> int:
        return sum(i.total_cents for (inst, _), i in self._invoices.items() if inst == installation_id and i.status == "paid")

"""API Consumer Billing Invoice — generate and manage billing invoices."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"

@dataclass
class LineItem:
    description: str
    quantity: int
    unit_price_cents: int
    total_cents: int = 0

    def __post_init__(self) -> None:
        self.total_cents = self.quantity * self.unit_price_cents

@dataclass
class Invoice:
    invoice_id: str
    consumer_id: str
    period: str  # "2024-01"
    status: InvoiceStatus = InvoiceStatus.DRAFT
    line_items: list[LineItem] = field(default_factory=list)
    issued_at: float = 0.0
    due_at: float = 0.0
    paid_at: float = 0.0

    @property
    def total_cents(self) -> int:
        return sum(item.total_cents for item in self.line_items)

    @property
    def total_dollars(self) -> str:
        return f"${self.total_cents / 100:.2f}"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerBillingInvoice:
    def __init__(self) -> None:
        self._invoices: dict[tuple[str, str], Invoice] = {}

    def create_invoice(self, installation_id: str, invoice: Invoice) -> Invoice:
        if not installation_id: raise ValueError("installation_id is required")
        if not invoice.line_items: raise ValueError("Invoice must have at least one line item")
        key = (installation_id, invoice.invoice_id)
        if key in self._invoices: raise ValueError(f"Invoice {invoice.invoice_id} exists")
        self._invoices[key] = invoice
        return invoice

    def issue(self, installation_id: str, invoice_id: str, due_days: int = 30) -> Invoice:
        inv = self._get(installation_id, invoice_id)
        if inv.status != InvoiceStatus.DRAFT: raise ValueError("Only draft invoices can be issued")
        inv.status = InvoiceStatus.ISSUED
        inv.issued_at = time.time()
        inv.due_at = inv.issued_at + due_days * 86400
        return inv

    def mark_paid(self, installation_id: str, invoice_id: str) -> Invoice:
        inv = self._get(installation_id, invoice_id)
        if inv.status not in (InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE): raise ValueError("Invoice not payable")
        inv.status = InvoiceStatus.PAID
        inv.paid_at = time.time()
        return inv

    def void(self, installation_id: str, invoice_id: str) -> Invoice:
        inv = self._get(installation_id, invoice_id)
        if inv.status == InvoiceStatus.PAID: raise ValueError("Cannot void paid invoice")
        inv.status = InvoiceStatus.VOID
        return inv

    def outstanding(self, installation_id: str) -> list[Invoice]:
        return [i for (inst, _), i in self._invoices.items() if inst == installation_id and i.status in (InvoiceStatus.ISSUED, InvoiceStatus.OVERDUE)]

    def list_invoices(self, installation_id: str, consumer_id: str | None = None) -> list[Invoice]:
        invoices = [i for (inst, _), i in self._invoices.items() if inst == installation_id]
        if consumer_id: invoices = [i for i in invoices if i.consumer_id == consumer_id]
        return invoices

    def _get(self, installation_id: str, invoice_id: str) -> Invoice:
        inv = self._invoices.get((installation_id, invoice_id))
        if inv is None: raise KeyError(f"Invoice {invoice_id} not found")
        return inv

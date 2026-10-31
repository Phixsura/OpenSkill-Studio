"""App Org Billing — track billing and invoicing for installed apps.

Manages billing records per installation:
- Create invoices with line items
- Track payment status
- Compute totals and outstanding balance
- Per-installation scoped billing
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"


@dataclass
class LineItem:
    """An invoice line item."""

    description: str
    quantity: float
    unit_price_cents: int
    total_cents: int = 0

    def __post_init__(self) -> None:
        self.total_cents = int(self.quantity * self.unit_price_cents)


@dataclass
class Invoice:
    """A billing invoice."""

    invoice_id: str
    installation_id: str
    items: list[LineItem] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    created_at: float = field(default_factory=time.time)
    due_date: str = ""
    paid_at: float | None = None

    @property
    def total_cents(self) -> int:
        return sum(item.total_cents for item in self.items)

    @property
    def total_dollars(self) -> float:
        return self.total_cents / 100


class AppOrgBilling:
    """Track billing and invoicing for installed apps."""

    def __init__(self) -> None:
        self._invoices: dict[tuple[str, str], Invoice] = {}

    def create_invoice(
        self,
        installation_id: str,
        invoice_id: str,
        items: list[dict],
        due_date: str = "",
        now: float | None = None,
    ) -> Invoice:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not invoice_id:
            raise ValueError("invoice_id is required")
        if not items:
            raise ValueError("at least one line item is required")

        key = (installation_id, invoice_id)
        if key in self._invoices:
            raise ValueError(f"Invoice {invoice_id} already exists")

        line_items = [
            LineItem(
                description=i["description"],
                quantity=i.get("quantity", 1),
                unit_price_cents=i["unit_price_cents"],
            )
            for i in items
        ]

        invoice = Invoice(
            invoice_id=invoice_id, installation_id=installation_id,
            items=line_items, due_date=due_date,
            created_at=now or time.time(),
        )
        self._invoices[key] = invoice
        return invoice

    def send_invoice(self, installation_id: str, invoice_id: str) -> Invoice:
        inv = self._get(installation_id, invoice_id)
        if inv.status != InvoiceStatus.DRAFT:
            raise ValueError(f"Cannot send invoice in {inv.status} state")
        inv.status = InvoiceStatus.SENT
        return inv

    def pay_invoice(self, installation_id: str, invoice_id: str) -> Invoice:
        inv = self._get(installation_id, invoice_id)
        if inv.status not in (InvoiceStatus.SENT, InvoiceStatus.OVERDUE):
            raise ValueError(f"Cannot pay invoice in {inv.status} state")
        inv.status = InvoiceStatus.PAID
        inv.paid_at = time.time()
        return inv

    def void_invoice(self, installation_id: str, invoice_id: str) -> Invoice:
        inv = self._get(installation_id, invoice_id)
        if inv.status == InvoiceStatus.PAID:
            raise ValueError("Cannot void a paid invoice")
        inv.status = InvoiceStatus.VOID
        return inv

    def get_invoice(self, installation_id: str, invoice_id: str) -> Invoice:
        return self._get(installation_id, invoice_id)

    def list_invoices(self, installation_id: str, status: InvoiceStatus | None = None) -> list[Invoice]:
        invoices = [inv for (inst, _), inv in self._invoices.items() if inst == installation_id]
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
        return invoices

    def outstanding_balance_cents(self, installation_id: str) -> int:
        return sum(
            inv.total_cents for inv in self.list_invoices(installation_id)
            if inv.status in (InvoiceStatus.SENT, InvoiceStatus.OVERDUE)
        )

    def _get(self, installation_id: str, invoice_id: str) -> Invoice:
        key = (installation_id, invoice_id)
        inv = self._invoices.get(key)
        if inv is None:
            raise KeyError(f"Invoice {invoice_id} not found")
        return inv

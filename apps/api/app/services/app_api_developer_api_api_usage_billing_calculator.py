"""App API Developer Usage Billing Calculator — calculate usage-based billing."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class BillingLineItem:
    item_id: str
    description: str
    quantity: int
    unit_price_cents: int
    total_cents: int = 0

    def __post_init__(self):
        self.total_cents = self.quantity * self.unit_price_cents

@dataclass
class BillingInvoice:
    invoice_id: str
    period: str  # "2025-01"
    line_items: list[BillingLineItem] = field(default_factory=list)
    discount_pct: float = 0.0

    @property
    def subtotal_cents(self) -> int:
        return sum(li.total_cents for li in self.line_items)

    @property
    def discount_cents(self) -> int:
        return int(self.subtotal_cents * self.discount_pct / 100)

    @property
    def total_cents(self) -> int:
        return self.subtotal_cents - self.discount_cents

class AppAPIDeveloperAPIApiUsageBillingCalculator:
    def __init__(self) -> None:
        self._invoices: dict[tuple[str, str], BillingInvoice] = {}

    def create_invoice(self, installation_id: str, invoice_id: str, period: str, line_items: list[dict], discount_pct: float = 0.0) -> BillingInvoice:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= discount_pct <= 100: raise ValueError("discount must be 0-100")
        items = [BillingLineItem(item_id=li["item_id"], description=li["description"], quantity=li["quantity"], unit_price_cents=li["unit_price_cents"]) for li in line_items]
        inv = BillingInvoice(invoice_id=invoice_id, period=period, line_items=items, discount_pct=discount_pct)
        self._invoices[(installation_id, invoice_id)] = inv
        return inv

    def get_invoice(self, installation_id: str, invoice_id: str) -> BillingInvoice:
        key = (installation_id, invoice_id)
        inv = self._invoices.get(key)
        if inv is None: raise KeyError(f"Invoice {invoice_id} not found")
        return inv

    def total_revenue_cents(self, installation_id: str) -> int:
        return sum(inv.total_cents for (inst, _), inv in self._invoices.items() if inst == installation_id)

    def list_invoices(self, installation_id: str) -> list[BillingInvoice]:
        return [inv for (inst, _), inv in self._invoices.items() if inst == installation_id]

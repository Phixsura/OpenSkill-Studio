"""Marketplace Billing Portal — manage subscriptions and invoices."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Invoice:
    invoice_id: str
    developer_id: str
    amount_cents: int
    status: str = "pending"  # pending, paid, overdue, cancelled
    description: str = ""
    created_at: float = 0.0
    paid_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


@dataclass
class Subscription:
    sub_id: str
    developer_id: str
    plan_id: str
    status: str = "active"  # active, cancelled, past_due
    current_period_end: float = 0.0


class BillingPortalService:
    def __init__(self):
        self._invoices: dict[str, Invoice] = {}
        self._subscriptions: dict[str, Subscription] = {}  # dev_id -> sub
        self._counter = 0

    def create_invoice(self, developer_id: str, amount_cents: int,
                       description: str = "") -> Invoice:
        self._counter += 1
        inv = Invoice(invoice_id=f"inv-{self._counter}", developer_id=developer_id,
                      amount_cents=amount_cents, description=description)
        self._invoices[inv.invoice_id] = inv
        return inv

    def pay_invoice(self, invoice_id: str) -> bool:
        inv = self._invoices.get(invoice_id)
        if not inv or inv.status != "pending": return False
        inv.status = "paid"
        inv.paid_at = time.time()
        return True

    def subscribe(self, developer_id: str, plan_id: str) -> Subscription:
        self._counter += 1
        sub = Subscription(sub_id=f"sub-{self._counter}", developer_id=developer_id,
                           plan_id=plan_id,
                           current_period_end=time.time() + 30 * 86400)
        self._subscriptions[developer_id] = sub
        return sub

    def cancel_subscription(self, developer_id: str) -> bool:
        sub = self._subscriptions.get(developer_id)
        if not sub or sub.status != "active": return False
        sub.status = "cancelled"
        return True

    def get_invoices(self, developer_id: str) -> list[Invoice]:
        return [i for i in self._invoices.values() if i.developer_id == developer_id]

    def get_subscription(self, developer_id: str) -> Subscription | None:
        return self._subscriptions.get(developer_id)

    def get_total_revenue(self) -> int:
        return sum(i.amount_cents for i in self._invoices.values() if i.status == "paid")

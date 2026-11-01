"""Developer Payout — calculate and process developer payouts.

Manages payout schedules, minimum thresholds, tax withholding,
payment method validation, and payout history with status tracking.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"


@dataclass
class PayoutConfig:
    developer_id: str
    payment_method: PaymentMethod
    min_threshold_cents: int = 5000  # $50 minimum
    tax_rate: float = 0.0
    tax_id: str = ""
    currency: str = "USD"


@dataclass
class Payout:
    payout_id: str
    developer_id: str
    gross_cents: int
    tax_cents: int
    net_cents: int
    status: PayoutStatus = PayoutStatus.PENDING
    payment_method: PaymentMethod = PaymentMethod.STRIPE
    reference: str = ""
    created_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class DeveloperPayoutService:
    """Manages developer payouts with tax and threshold logic."""

    PLATFORM_FEE = 0.15

    def __init__(self):
        self._configs: dict[str, PayoutConfig] = {}
        self._payouts: list[Payout] = []
        self._balances: dict[str, int] = defaultdict(int)

    def configure(self, developer_id: str, payment_method: PaymentMethod,
                  min_threshold_cents: int = 5000,
                  tax_rate: float = 0.0, tax_id: str = "") -> PayoutConfig:
        if tax_rate < 0 or tax_rate > 0.5:
            raise ValueError("Tax rate must be 0-50%")
        config = PayoutConfig(
            developer_id=developer_id, payment_method=payment_method,
            min_threshold_cents=max(1000, min_threshold_cents),
            tax_rate=tax_rate, tax_id=tax_id,
        )
        self._configs[developer_id] = config
        return config

    def add_earnings(self, developer_id: str, amount_cents: int) -> int:
        if amount_cents <= 0:
            raise ValueError("Earnings must be positive")
        # Deduct platform fee
        dev_share = int(amount_cents * (1 - self.PLATFORM_FEE))
        self._balances[developer_id] += dev_share
        return self._balances[developer_id]

    def get_balance(self, developer_id: str) -> int:
        return self._balances.get(developer_id, 0)

    def request_payout(self, developer_id: str) -> Payout | dict:
        config = self._configs.get(developer_id)
        if not config:
            return {"error": "No payout config — set up payment method first"}

        balance = self._balances.get(developer_id, 0)
        if balance < config.min_threshold_cents:
            return {"error": f"Balance {balance} below minimum {config.min_threshold_cents}"}

        tax_cents = int(balance * config.tax_rate)
        net_cents = balance - tax_cents

        payout = Payout(
            payout_id=f"po_{secrets.token_urlsafe(10)}",
            developer_id=developer_id,
            gross_cents=balance, tax_cents=tax_cents,
            net_cents=net_cents, payment_method=config.payment_method,
        )
        self._payouts.append(payout)
        self._balances[developer_id] = 0
        return payout

    def complete_payout(self, payout_id: str, reference: str = "") -> bool:
        payout = next((p for p in self._payouts if p.payout_id == payout_id), None)
        if not payout or payout.status != PayoutStatus.PENDING:
            return False
        payout.status = PayoutStatus.COMPLETED
        payout.reference = reference
        payout.completed_at = datetime.now(timezone.utc).isoformat()
        return True

    def fail_payout(self, payout_id: str) -> bool:
        payout = next((p for p in self._payouts if p.payout_id == payout_id), None)
        if not payout or payout.status != PayoutStatus.PENDING:
            return False
        payout.status = PayoutStatus.FAILED
        # Refund balance
        self._balances[payout.developer_id] += payout.gross_cents
        return True

    def get_history(self, developer_id: str) -> list[Payout]:
        return [p for p in self._payouts if p.developer_id == developer_id]

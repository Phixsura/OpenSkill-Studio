"""Revenue Analytics — track and analyze extension marketplace revenue.

Monitors subscription revenue, one-time purchases, refunds, MRR/ARR
calculations, revenue by tier, and developer payout tracking.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TransactionType(str, Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    REFUND = "refund"
    PAYOUT = "payout"


@dataclass
class RevenueTransaction:
    tx_id: str
    extension_id: str
    developer_id: str
    amount_cents: int
    tx_type: TransactionType
    tier: str = ""
    currency: str = "USD"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class RevenueAnalyticsService:
    """Tracks marketplace revenue with MRR/ARR and payout calculations."""

    PLATFORM_FEE_RATE = 0.15  # 15% platform fee

    def __init__(self):
        self._transactions: list[RevenueTransaction] = []

    def record(self, extension_id: str, developer_id: str,
               amount_cents: int, tx_type: TransactionType,
               tier: str = "") -> RevenueTransaction:
        if amount_cents < 0 and tx_type != TransactionType.REFUND:
            raise ValueError("Only refunds can be negative")
        tx = RevenueTransaction(
            tx_id=f"tx_{secrets.token_urlsafe(10)}",
            extension_id=extension_id, developer_id=developer_id,
            amount_cents=amount_cents, tx_type=tx_type, tier=tier,
        )
        self._transactions.append(tx)
        return tx

    def get_mrr(self, extension_id: str) -> int:
        """Monthly Recurring Revenue in cents."""
        return sum(
            t.amount_cents for t in self._transactions
            if t.extension_id == extension_id
            and t.tx_type == TransactionType.SUBSCRIPTION
        )

    def get_total_revenue(self, extension_id: str) -> dict:
        txs = [t for t in self._transactions if t.extension_id == extension_id]
        gross = sum(t.amount_cents for t in txs if t.tx_type in (TransactionType.SUBSCRIPTION, TransactionType.ONE_TIME))
        refunds = sum(abs(t.amount_cents) for t in txs if t.tx_type == TransactionType.REFUND)
        net = gross - refunds
        return {
            "gross_cents": gross,
            "refunds_cents": refunds,
            "net_cents": net,
            "platform_fee_cents": int(net * self.PLATFORM_FEE_RATE),
            "developer_cents": int(net * (1 - self.PLATFORM_FEE_RATE)),
        }

    def get_revenue_by_tier(self, extension_id: str) -> dict[str, int]:
        by_tier: dict[str, int] = defaultdict(int)
        for t in self._transactions:
            if t.extension_id == extension_id and t.tier and t.tx_type != TransactionType.REFUND:
                by_tier[t.tier] += t.amount_cents
        return dict(by_tier)

    def get_developer_earnings(self, developer_id: str) -> dict:
        txs = [t for t in self._transactions if t.developer_id == developer_id]
        gross = sum(t.amount_cents for t in txs
                    if t.tx_type in (TransactionType.SUBSCRIPTION, TransactionType.ONE_TIME))
        refunds = sum(abs(t.amount_cents) for t in txs if t.tx_type == TransactionType.REFUND)
        payouts = sum(abs(t.amount_cents) for t in txs if t.tx_type == TransactionType.PAYOUT)
        net = gross - refunds
        owed = int(net * (1 - self.PLATFORM_FEE_RATE)) - payouts
        return {
            "gross_cents": gross, "refunds_cents": refunds,
            "net_cents": net, "payouts_cents": payouts,
            "owed_cents": max(0, owed),
        }

    def get_top_extensions(self, limit: int = 10) -> list[dict]:
        by_ext: dict[str, int] = defaultdict(int)
        for t in self._transactions:
            if t.tx_type in (TransactionType.SUBSCRIPTION, TransactionType.ONE_TIME):
                by_ext[t.extension_id] += t.amount_cents
        sorted_exts = sorted(by_ext.items(), key=lambda x: x[1], reverse=True)
        return [{"extension_id": eid, "revenue_cents": rev}
                for eid, rev in sorted_exts[:limit]]

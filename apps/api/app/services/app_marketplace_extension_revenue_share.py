"""Extension Revenue Share — calculate and track developer payouts."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class RevenueTx:
    tx_id: str
    extension_id: str
    developer_id: str
    gross_cents: int
    platform_fee_pct: float
    net_cents: int = 0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()
        if not self.net_cents:
            self.net_cents = round(self.gross_cents * (1 - self.platform_fee_pct / 100))


class ExtRevenueShareService:
    DEFAULT_FEE = 15.0  # 15% platform fee

    def __init__(self):
        self._transactions: list[RevenueTx] = []
        self._fee_overrides: dict[str, float] = {}  # dev_id -> custom fee
        self._counter = 0

    def set_fee(self, developer_id: str, fee_pct: float) -> None:
        if fee_pct < 0 or fee_pct > 50:
            raise ValueError("Fee must be 0-50%")
        self._fee_overrides[developer_id] = fee_pct

    def record_sale(self, extension_id: str, developer_id: str,
                    gross_cents: int) -> RevenueTx:
        fee = self._fee_overrides.get(developer_id, self.DEFAULT_FEE)
        self._counter += 1
        tx = RevenueTx(tx_id=f"rev-{self._counter}", extension_id=extension_id,
                       developer_id=developer_id, gross_cents=gross_cents,
                       platform_fee_pct=fee)
        self._transactions.append(tx)
        return tx

    def get_developer_earnings(self, developer_id: str) -> dict:
        txs = [t for t in self._transactions if t.developer_id == developer_id]
        return {
            "total_gross": sum(t.gross_cents for t in txs),
            "total_net": sum(t.net_cents for t in txs),
            "total_fees": sum(t.gross_cents - t.net_cents for t in txs),
            "transaction_count": len(txs),
        }

    def get_platform_revenue(self) -> dict:
        return {
            "total_gross": sum(t.gross_cents for t in self._transactions),
            "total_fees": sum(t.gross_cents - t.net_cents for t in self._transactions),
            "total_payouts": sum(t.net_cents for t in self._transactions),
        }

"""Consumer API Credit System — manage prepaid API credits."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class CreditTransaction:
    transaction_id: str
    consumer_id: str
    amount: int  # positive = add, negative = deduct
    balance_after: int
    reason: str
    timestamp: datetime

@dataclass
class CreditBalance:
    consumer_id: str
    balance: int
    total_purchased: int
    total_consumed: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerCreditSystem:
    def __init__(self) -> None:
        self._balances: dict[tuple[str, str], int] = {}
        self._purchased: dict[tuple[str, str], int] = {}
        self._consumed: dict[tuple[str, str], int] = {}
        self._transactions: dict[tuple[str, str], list[CreditTransaction]] = {}

    def add_credits(self, installation_id: str, consumer_id: str, amount: int, reason: str, now: datetime) -> CreditTransaction:
        if not installation_id:
            raise ValueError("installation_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        key = (installation_id, consumer_id)
        self._balances[key] = self._balances.get(key, 0) + amount
        self._purchased[key] = self._purchased.get(key, 0) + amount
        tx = CreditTransaction(transaction_id=f"tx-{now.isoformat()}", consumer_id=consumer_id, amount=amount, balance_after=self._balances[key], reason=reason, timestamp=now)
        if key not in self._transactions:
            self._transactions[key] = []
        self._transactions[key].append(tx)
        return tx

    def consume(self, installation_id: str, consumer_id: str, amount: int, reason: str, now: datetime) -> CreditTransaction:
        if amount <= 0:
            raise ValueError("amount must be positive")
        key = (installation_id, consumer_id)
        balance = self._balances.get(key, 0)
        if balance < amount:
            raise ValueError(f"Insufficient credits: {balance} < {amount}")
        self._balances[key] = balance - amount
        self._consumed[key] = self._consumed.get(key, 0) + amount
        tx = CreditTransaction(transaction_id=f"tx-{now.isoformat()}", consumer_id=consumer_id, amount=-amount, balance_after=self._balances[key], reason=reason, timestamp=now)
        if key not in self._transactions:
            self._transactions[key] = []
        self._transactions[key].append(tx)
        return tx

    def get_balance(self, installation_id: str, consumer_id: str) -> CreditBalance:
        key = (installation_id, consumer_id)
        return CreditBalance(consumer_id=consumer_id, balance=self._balances.get(key, 0), total_purchased=self._purchased.get(key, 0), total_consumed=self._consumed.get(key, 0))

    def get_transactions(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[CreditTransaction]:
        return self._transactions.get((installation_id, consumer_id), [])[-limit:]

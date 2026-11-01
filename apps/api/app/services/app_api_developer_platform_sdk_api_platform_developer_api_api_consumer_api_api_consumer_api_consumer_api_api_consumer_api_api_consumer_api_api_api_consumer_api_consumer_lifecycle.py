"""Consumer API Consumer Lifecycle — manage consumer account lifecycle states."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerAccount:
    consumer_id: str
    name: str
    status: str = "pending"  # "pending", "active", "suspended", "deactivated", "deleted"
    plan: str = "free"
    created_at: datetime | None = None
    activated_at: datetime | None = None
    suspended_at: datetime | None = None
    deactivated_at: datetime | None = None
    suspension_reason: str = ""

VALID_TRANSITIONS = {
    "pending": {"active"},
    "active": {"suspended", "deactivated"},
    "suspended": {"active", "deactivated"},
    "deactivated": {"active"},
}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle:
    def __init__(self) -> None:
        self._accounts: dict[tuple[str, str], ConsumerAccount] = {}

    def create(self, installation_id: str, account: ConsumerAccount) -> ConsumerAccount:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not account.name:
            raise ValueError("name is required")
        key = (installation_id, account.consumer_id)
        if key in self._accounts:
            raise ValueError(f"Consumer {account.consumer_id} already exists")
        account.status = "pending"
        account.created_at = account.created_at or datetime.utcnow()
        self._accounts[key] = account
        return account

    def transition(self, installation_id: str, consumer_id: str, new_status: str, reason: str = "", now: datetime | None = None) -> ConsumerAccount:
        now = now or datetime.utcnow()
        key = (installation_id, consumer_id)
        account = self._accounts.get(key)
        if not account:
            raise ValueError("Consumer not found")
        allowed = VALID_TRANSITIONS.get(account.status, set())
        if new_status not in allowed:
            raise ValueError(f"Cannot transition from {account.status} to {new_status}")
        account.status = new_status
        if new_status == "active":
            account.activated_at = now
        elif new_status == "suspended":
            account.suspended_at = now
            account.suspension_reason = reason
        elif new_status == "deactivated":
            account.deactivated_at = now
        return account

    def get(self, installation_id: str, consumer_id: str) -> ConsumerAccount | None:
        return self._accounts.get((installation_id, consumer_id))

    def list_by_status(self, installation_id: str, status: str | None = None) -> list[ConsumerAccount]:
        accounts = [a for (inst, _), a in self._accounts.items() if inst == installation_id]
        if status:
            accounts = [a for a in accounts if a.status == status]
        return sorted(accounts, key=lambda a: a.name)

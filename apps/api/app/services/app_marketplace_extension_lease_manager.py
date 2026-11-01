"""Lease Manager — time-bounded resource ownership with renewal.

Used in distributed systems to prevent indefinite resource holding.
If a holder crashes, the lease expires and another can claim.

Implements:
- Acquire lease with TTL
- Renew before expiry (heartbeat)
- Auto-expire stale leases
- Lease transfer (graceful handoff)
- Fencing token for stale-lease protection
- Lease contention tracking
"""
from __future__ import annotations
from dataclasses import dataclass
import time
import secrets


@dataclass
class Lease:
    lease_id: str
    resource: str
    holder: str
    fencing_token: int
    acquired_at: float
    expires_at: float
    renewed_count: int = 0


class LeaseManagerService:
    def __init__(self):
        self._leases: dict[str, Lease] = {}  # resource → lease
        self._fencing_counter = 0
        self._contention: dict[str, int] = {}  # resource → failed acquire count

    def acquire(self, resource: str, holder: str,
                ttl_seconds: float = 30) -> Lease | None:
        """Acquire a lease. Returns None if held by another."""
        now = time.time()
        existing = self._leases.get(resource)

        # Expire stale lease
        if existing and existing.expires_at <= now:
            del self._leases[resource]
            existing = None

        if existing:
            if existing.holder == holder:
                return self.renew(resource, holder, ttl_seconds)
            self._contention[resource] = self._contention.get(resource, 0) + 1
            return None  # held by another

        self._fencing_counter += 1
        lease = Lease(
            lease_id=secrets.token_hex(8),
            resource=resource, holder=holder,
            fencing_token=self._fencing_counter,
            acquired_at=now, expires_at=now + ttl_seconds)
        self._leases[resource] = lease
        return lease

    def renew(self, resource: str, holder: str,
              ttl_seconds: float = 30) -> Lease | None:
        """Renew a lease. Only the holder can renew."""
        lease = self._leases.get(resource)
        if not lease or lease.holder != holder:
            return None
        now = time.time()
        if lease.expires_at <= now:
            del self._leases[resource]
            return None  # expired, must re-acquire
        lease.expires_at = now + ttl_seconds
        lease.renewed_count += 1
        return lease

    def release(self, resource: str, holder: str) -> bool:
        """Gracefully release a lease."""
        lease = self._leases.get(resource)
        if lease and lease.holder == holder:
            del self._leases[resource]
            return True
        return False

    def transfer(self, resource: str, from_holder: str,
                 to_holder: str, ttl_seconds: float = 30) -> Lease | None:
        """Transfer a lease to another holder."""
        lease = self._leases.get(resource)
        if not lease or lease.holder != from_holder:
            return None
        self.release(resource, from_holder)
        return self.acquire(resource, to_holder, ttl_seconds)

    def is_valid(self, resource: str, holder: str,
                 fencing_token: int = 0) -> bool:
        """Check if a lease is still valid."""
        lease = self._leases.get(resource)
        if not lease or lease.holder != holder:
            return False
        if lease.expires_at <= time.time():
            return False
        if fencing_token and lease.fencing_token != fencing_token:
            return False
        return True

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [r for r, l in self._leases.items() if l.expires_at <= now]
        for r in expired:
            del self._leases[r]
        return len(expired)

    def get_contention(self) -> dict[str, int]:
        return dict(self._contention)

    def get_all_leases(self) -> list[dict]:
        now = time.time()
        return [{"resource": l.resource, "holder": l.holder,
                 "fencing_token": l.fencing_token,
                 "remaining_seconds": round(l.expires_at - now, 1),
                 "renewed": l.renewed_count}
                for l in self._leases.values() if l.expires_at > now]

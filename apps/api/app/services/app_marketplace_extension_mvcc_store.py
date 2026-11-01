"""MVCC Store — Multi-Version Concurrency Control for snapshot isolation.

Implements:
- Each write creates a new version (never overwrites)
- Transactions see a consistent snapshot at their start time
- Write-write conflict detection
- Garbage collection of old versions
- Version history per key
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Version:
    key: str
    value: object
    tx_id: str
    timestamp: float
    deleted: bool = False


@dataclass
class MvccTransaction:
    tx_id: str
    snapshot_time: float
    writes: dict[str, object] = field(default_factory=dict)
    deletes: set[str] = field(default_factory=set)
    committed: bool = False
    aborted: bool = False


class MvccStoreService:
    def __init__(self):
        self._versions: dict[str, list[Version]] = {}  # key -> [versions] newest last
        self._transactions: dict[str, MvccTransaction] = {}
        self._tx_counter = 0

    def begin(self) -> MvccTransaction:
        self._tx_counter += 1
        tx = MvccTransaction(tx_id=f"mvcc-{self._tx_counter}",
                             snapshot_time=time.time())
        self._transactions[tx.tx_id] = tx
        return tx

    def read(self, tx_id: str, key: str) -> object | None:
        """Read the version visible at this transaction's snapshot."""
        tx = self._transactions.get(tx_id)
        if not tx or tx.aborted:
            raise ValueError("Transaction not active")

        # Check local writes first (read-your-own-writes)
        if key in tx.deletes:
            return None
        if key in tx.writes:
            return tx.writes[key]

        # Find the latest version visible at snapshot time
        versions = self._versions.get(key, [])
        for v in reversed(versions):
            if v.timestamp <= tx.snapshot_time:
                return None if v.deleted else v.value
        return None

    def write(self, tx_id: str, key: str, value: object) -> None:
        tx = self._transactions.get(tx_id)
        if not tx or tx.committed or tx.aborted:
            raise ValueError("Transaction not active")
        tx.writes[key] = value
        tx.deletes.discard(key)

    def delete(self, tx_id: str, key: str) -> None:
        tx = self._transactions.get(tx_id)
        if not tx or tx.committed or tx.aborted:
            raise ValueError("Transaction not active")
        tx.deletes.add(key)
        tx.writes.pop(key, None)

    def commit(self, tx_id: str) -> bool:
        """Commit transaction. Returns False on write-write conflict."""
        tx = self._transactions.get(tx_id)
        if not tx or tx.committed or tx.aborted:
            return False

        now = time.time()

        # Write-write conflict detection
        for key in list(tx.writes.keys()) + list(tx.deletes):
            versions = self._versions.get(key, [])
            # Check if another transaction wrote this key after our snapshot
            for v in versions:
                if v.timestamp > tx.snapshot_time and v.tx_id != tx_id:
                    tx.aborted = True
                    return False  # conflict!

        # Apply writes
        for key, value in tx.writes.items():
            if key not in self._versions:
                self._versions[key] = []
            self._versions[key].append(Version(
                key=key, value=value, tx_id=tx_id, timestamp=now))

        # Apply deletes
        for key in tx.deletes:
            if key not in self._versions:
                self._versions[key] = []
            self._versions[key].append(Version(
                key=key, value=None, tx_id=tx_id, timestamp=now, deleted=True))

        tx.committed = True
        return True

    def abort(self, tx_id: str) -> None:
        tx = self._transactions.get(tx_id)
        if tx:
            tx.aborted = True
            tx.writes.clear()
            tx.deletes.clear()

    def gc(self, keep_versions: int = 2) -> int:
        """Garbage collect old versions, keeping N newest per key."""
        removed = 0
        for key in self._versions:
            versions = self._versions[key]
            if len(versions) > keep_versions:
                to_remove = len(versions) - keep_versions
                self._versions[key] = versions[to_remove:]
                removed += to_remove
        return removed

    def get_version_count(self, key: str) -> int:
        return len(self._versions.get(key, []))

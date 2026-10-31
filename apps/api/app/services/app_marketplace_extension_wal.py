"""Write-Ahead Log — crash recovery via sequential log with checkpointing.

Implements:
- Append-only log entries with LSN (Log Sequence Number)
- Transaction begin/commit/abort tracking
- Checkpoint: snapshot state + truncate log
- Recovery: replay uncommitted transactions from last checkpoint
- Log compaction
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from enum import Enum


class TxState(str, Enum):
    ACTIVE = "active"
    COMMITTED = "committed"
    ABORTED = "aborted"


@dataclass
class WalEntry:
    lsn: int  # Log Sequence Number
    tx_id: str
    operation: str  # begin, write, delete, commit, abort, checkpoint
    key: str = ""
    value: str = ""
    timestamp: float = 0.0


@dataclass
class Checkpoint:
    lsn: int
    state: dict  # snapshot of committed state
    active_txs: list[str]
    timestamp: float = 0.0


class WriteAheadLogService:
    def __init__(self):
        self._log: list[WalEntry] = []
        self._lsn = 0
        self._transactions: dict[str, TxState] = {}
        self._tx_writes: dict[str, list[WalEntry]] = {}  # tx_id -> pending writes
        self._committed_state: dict[str, str] = {}  # the "database"
        self._last_checkpoint: Checkpoint | None = None

    def _next_lsn(self) -> int:
        self._lsn += 1
        return self._lsn

    def begin(self, tx_id: str) -> WalEntry:
        if tx_id in self._transactions:
            raise ValueError(f"Transaction {tx_id} already exists")
        entry = WalEntry(lsn=self._next_lsn(), tx_id=tx_id,
                         operation="begin", timestamp=time.time())
        self._log.append(entry)
        self._transactions[tx_id] = TxState.ACTIVE
        self._tx_writes[tx_id] = []
        return entry

    def write(self, tx_id: str, key: str, value: str) -> WalEntry:
        if self._transactions.get(tx_id) != TxState.ACTIVE:
            raise ValueError(f"Transaction {tx_id} not active")
        entry = WalEntry(lsn=self._next_lsn(), tx_id=tx_id,
                         operation="write", key=key, value=value,
                         timestamp=time.time())
        self._log.append(entry)
        self._tx_writes[tx_id].append(entry)
        return entry

    def delete(self, tx_id: str, key: str) -> WalEntry:
        if self._transactions.get(tx_id) != TxState.ACTIVE:
            raise ValueError(f"Transaction {tx_id} not active")
        entry = WalEntry(lsn=self._next_lsn(), tx_id=tx_id,
                         operation="delete", key=key, timestamp=time.time())
        self._log.append(entry)
        self._tx_writes[tx_id].append(entry)
        return entry

    def commit(self, tx_id: str) -> WalEntry:
        if self._transactions.get(tx_id) != TxState.ACTIVE:
            raise ValueError(f"Transaction {tx_id} not active")
        # Apply writes to committed state
        for w in self._tx_writes.get(tx_id, []):
            if w.operation == "write":
                self._committed_state[w.key] = w.value
            elif w.operation == "delete":
                self._committed_state.pop(w.key, None)

        entry = WalEntry(lsn=self._next_lsn(), tx_id=tx_id,
                         operation="commit", timestamp=time.time())
        self._log.append(entry)
        self._transactions[tx_id] = TxState.COMMITTED
        del self._tx_writes[tx_id]
        return entry

    def abort(self, tx_id: str) -> WalEntry:
        if self._transactions.get(tx_id) != TxState.ACTIVE:
            raise ValueError(f"Transaction {tx_id} not active")
        entry = WalEntry(lsn=self._next_lsn(), tx_id=tx_id,
                         operation="abort", timestamp=time.time())
        self._log.append(entry)
        self._transactions[tx_id] = TxState.ABORTED
        del self._tx_writes[tx_id]
        return entry

    def checkpoint(self) -> Checkpoint:
        """Snapshot current state and truncate log."""
        active = [tx for tx, state in self._transactions.items()
                  if state == TxState.ACTIVE]
        cp = Checkpoint(lsn=self._lsn, state=dict(self._committed_state),
                        active_txs=active, timestamp=time.time())
        self._last_checkpoint = cp
        # Truncate log — keep only entries after checkpoint for active txs
        if active:
            min_active_lsn = min(
                e.lsn for e in self._log if e.tx_id in active
            ) if any(e.tx_id in active for e in self._log) else self._lsn
            self._log = [e for e in self._log if e.lsn >= min_active_lsn]
        else:
            self._log = []
        return cp

    def recover(self) -> dict:
        """Recover state from checkpoint + replay log."""
        if self._last_checkpoint:
            state = dict(self._last_checkpoint.state)
            replay_from = self._last_checkpoint.lsn
        else:
            state = {}
            replay_from = 0

        # Replay committed transactions from log
        tx_writes: dict[str, list[WalEntry]] = {}
        committed_txs: set[str] = set()
        aborted_txs: set[str] = set()

        for entry in self._log:
            if entry.lsn <= replay_from and self._last_checkpoint:
                continue
            if entry.operation == "begin":
                tx_writes[entry.tx_id] = []
            elif entry.operation in ("write", "delete"):
                if entry.tx_id in tx_writes:
                    tx_writes[entry.tx_id].append(entry)
            elif entry.operation == "commit":
                committed_txs.add(entry.tx_id)
            elif entry.operation == "abort":
                aborted_txs.add(entry.tx_id)

        # Apply only committed transactions
        for tx_id in committed_txs:
            for w in tx_writes.get(tx_id, []):
                if w.operation == "write":
                    state[w.key] = w.value
                elif w.operation == "delete":
                    state.pop(w.key, None)

        return state

    def get_state(self) -> dict:
        return dict(self._committed_state)

    def get_log_size(self) -> int:
        return len(self._log)

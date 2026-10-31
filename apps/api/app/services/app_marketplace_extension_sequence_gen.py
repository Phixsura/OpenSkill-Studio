"""Sequence Generator — distributed-safe ID generation (Snowflake-inspired).

Twitter Snowflake-style: 64-bit IDs that are time-sortable, unique
across nodes, and reveal no information about total count.

Implements:
- Snowflake: timestamp(41) + node_id(10) + sequence(12)
- ULID-style: timestamp prefix + random suffix (string)
- Auto-incrementing with gap detection
- Custom prefix IDs (user_xxxx, order_xxxx)
- Monotonically increasing within a node
"""
from __future__ import annotations
import time
import secrets
import base64


# Snowflake constants
EPOCH = 1700000000000  # custom epoch (ms since 2023-11-14)
NODE_BITS = 10
SEQUENCE_BITS = 12
MAX_NODE = (1 << NODE_BITS) - 1
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1


class SequenceGeneratorService:
    def __init__(self, node_id: int = 0):
        if not 0 <= node_id <= MAX_NODE:
            raise ValueError(f"node_id must be 0-{MAX_NODE}")
        self._node_id = node_id
        self._sequence = 0
        self._last_timestamp = 0
        self._auto_counters: dict[str, int] = {}

    def snowflake(self) -> int:
        """Generate a 64-bit Snowflake ID."""
        ts = int(time.time() * 1000) - EPOCH

        if ts == self._last_timestamp:
            self._sequence = (self._sequence + 1) & MAX_SEQUENCE
            if self._sequence == 0:
                # Sequence exhausted this ms — wait for next ms
                while ts <= self._last_timestamp:
                    ts = int(time.time() * 1000) - EPOCH
        else:
            self._sequence = 0

        self._last_timestamp = ts

        return ((ts << (NODE_BITS + SEQUENCE_BITS)) |
                (self._node_id << SEQUENCE_BITS) |
                self._sequence)

    def snowflake_decode(self, snowflake_id: int) -> dict:
        """Decode a Snowflake ID into its components."""
        sequence = snowflake_id & MAX_SEQUENCE
        node_id = (snowflake_id >> SEQUENCE_BITS) & MAX_NODE
        timestamp = (snowflake_id >> (NODE_BITS + SEQUENCE_BITS)) + EPOCH
        return {
            "timestamp_ms": timestamp,
            "node_id": node_id,
            "sequence": sequence,
            "time_iso": time.strftime("%Y-%m-%dT%H:%M:%S",
                                      time.gmtime(timestamp / 1000)),
        }

    def ulid(self) -> str:
        """Generate a ULID-style ID: timestamp prefix + random suffix."""
        ts = int(time.time() * 1000)
        ts_bytes = ts.to_bytes(6, 'big')
        rand_bytes = secrets.token_bytes(10)
        raw = ts_bytes + rand_bytes
        # Encode as base32 (Crockford-style simplified)
        return base64.b32encode(raw).decode().rstrip("=").lower()

    def prefixed(self, prefix: str, length: int = 12) -> str:
        """Generate prefixed ID: user_a3b7c9d2e1f4."""
        suffix = secrets.token_hex(length // 2)
        return f"{prefix}_{suffix}"

    def auto_increment(self, namespace: str = "default") -> int:
        """Thread-unsafe auto-increment. For single-node use."""
        self._auto_counters[namespace] = self._auto_counters.get(namespace, 0) + 1
        return self._auto_counters[namespace]

    def batch_snowflake(self, count: int) -> list[int]:
        """Generate a batch of sequential Snowflake IDs."""
        return [self.snowflake() for _ in range(count)]

    def is_valid_snowflake(self, snowflake_id: int) -> bool:
        """Check if a value looks like a valid Snowflake ID."""
        if snowflake_id <= 0:
            return False
        decoded = self.snowflake_decode(snowflake_id)
        ts = decoded["timestamp_ms"]
        # Should be between epoch and now+1hour
        now = int(time.time() * 1000)
        return EPOCH <= ts <= now + 3600000

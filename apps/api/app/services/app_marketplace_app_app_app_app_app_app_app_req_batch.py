"""Request batching engine — batch multiple requests for efficient processing."""
from __future__ import annotations
import time


class RequestBatcher:
    def __init__(self, max_batch_size: int = 50, max_wait_ms: int = 100):
        self._max_size = max_batch_size
        self._max_wait = max_wait_ms
        self._buffer: list[dict] = []
        self._flushed = 0

    def add(self, request: dict) -> dict:
        self._buffer.append(request)
        if len(self._buffer) >= self._max_size:
            return self.flush()
        return {"buffered": True, "buffer_size": len(self._buffer)}

    def flush(self) -> dict:
        batch = list(self._buffer)
        self._buffer.clear()
        self._flushed += 1
        return {"flushed": True, "batch_size": len(batch),
                "batch_number": self._flushed, "requests": batch}

    def stats(self) -> dict:
        return {"buffer_size": len(self._buffer), "max_batch_size": self._max_size,
                "batches_flushed": self._flushed}

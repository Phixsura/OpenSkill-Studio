"""Consumer Sandbox Manager — isolated sandbox environments for testing."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class Sandbox:
    sandbox_id: str
    consumer_id: str
    name: str
    status: str = "active"  # active, paused, expired
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str | None = None
    api_key: str = field(default_factory=lambda: f"sb_{secrets.token_hex(16)}")
    request_count: int = 0
    max_requests: int = 10000
    data_isolated: bool = True


@dataclass
class SandboxManager:
    """Manage isolated sandbox environments for API testing."""

    _sandboxes: dict[str, Sandbox] = field(default_factory=dict)

    def create(self, consumer_id: str, name: str, max_requests: int = 10000,
               expires_at: str | None = None) -> dict:
        sandbox_id = f"sb-{secrets.token_hex(4)}"
        if max_requests < 1:
            raise ValueError("max_requests must be positive")
        sandbox = Sandbox(
            sandbox_id=sandbox_id, consumer_id=consumer_id, name=name,
            max_requests=max_requests, expires_at=expires_at,
        )
        self._sandboxes[sandbox_id] = sandbox
        logger.info("sandbox_created", sandbox_id=sandbox_id, consumer_id=consumer_id)
        return {"sandbox_id": sandbox_id, "api_key": sandbox.api_key, "name": name}

    def use_request(self, sandbox_id: str) -> dict:
        sb = self._sandboxes.get(sandbox_id)
        if not sb:
            return {"allowed": False, "reason": "not_found"}
        if sb.status != "active":
            return {"allowed": False, "reason": f"sandbox_{sb.status}"}
        if sb.request_count >= sb.max_requests:
            return {"allowed": False, "reason": "quota_exceeded"}
        sb.request_count += 1
        return {"allowed": True, "remaining": sb.max_requests - sb.request_count}

    def pause(self, sandbox_id: str) -> dict:
        sb = self._sandboxes.get(sandbox_id)
        if not sb:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        sb.status = "paused"
        return {"sandbox_id": sandbox_id, "status": "paused"}

    def resume(self, sandbox_id: str) -> dict:
        sb = self._sandboxes.get(sandbox_id)
        if not sb:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        if sb.status != "paused":
            raise ValueError("Can only resume paused sandboxes")
        sb.status = "active"
        return {"sandbox_id": sandbox_id, "status": "active"}

    def reset(self, sandbox_id: str) -> dict:
        sb = self._sandboxes.get(sandbox_id)
        if not sb:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        sb.request_count = 0
        sb.status = "active"
        sb.api_key = f"sb_{secrets.token_hex(16)}"
        return {"sandbox_id": sandbox_id, "reset": True, "new_api_key": sb.api_key}

    def delete(self, sandbox_id: str) -> dict:
        if sandbox_id not in self._sandboxes:
            return {"deleted": False}
        del self._sandboxes[sandbox_id]
        return {"deleted": True}

    def get_sandbox(self, sandbox_id: str) -> dict | None:
        sb = self._sandboxes.get(sandbox_id)
        if not sb:
            return None
        return {
            "sandbox_id": sb.sandbox_id, "consumer_id": sb.consumer_id,
            "name": sb.name, "status": sb.status,
            "request_count": sb.request_count, "max_requests": sb.max_requests,
            "usage_pct": round(sb.request_count / sb.max_requests * 100, 1),
            "api_key_prefix": sb.api_key[:8] + "...",
        }

    def list_sandboxes(self, consumer_id: str | None = None) -> list[dict]:
        sandboxes = list(self._sandboxes.values())
        if consumer_id:
            sandboxes = [s for s in sandboxes if s.consumer_id == consumer_id]
        return [self.get_sandbox(s.sandbox_id) for s in sandboxes]

    def get_stats(self) -> dict:
        all_sb = list(self._sandboxes.values())
        return {
            "total": len(all_sb),
            "active": sum(1 for s in all_sb if s.status == "active"),
            "paused": sum(1 for s in all_sb if s.status == "paused"),
            "total_requests": sum(s.request_count for s in all_sb),
        }

"""Developer Sandbox Quota — per-developer sandbox resource limits."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class SandboxQuota:
    developer_id: str
    max_sandboxes: int = 5
    max_memory_mb: int = 512
    max_cpu_seconds: int = 3600
    active_sandboxes: int = 0
    memory_used_mb: int = 0
    cpu_used_seconds: int = 0
    tier: str = "free"  # free, pro, enterprise


class DevSandboxQuotaService:
    TIER_LIMITS = {
        "free": {"sandboxes": 3, "memory": 256, "cpu": 1800},
        "pro": {"sandboxes": 10, "memory": 1024, "cpu": 7200},
        "enterprise": {"sandboxes": 50, "memory": 4096, "cpu": 36000},
    }

    def __init__(self):
        self._quotas: dict[str, SandboxQuota] = {}

    def get_or_create(self, developer_id: str, tier: str = "free") -> SandboxQuota:
        if developer_id not in self._quotas:
            limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS["free"])
            self._quotas[developer_id] = SandboxQuota(
                developer_id=developer_id, tier=tier,
                max_sandboxes=limits["sandboxes"],
                max_memory_mb=limits["memory"],
                max_cpu_seconds=limits["cpu"])
        return self._quotas[developer_id]

    def can_create_sandbox(self, developer_id: str) -> tuple[bool, str]:
        q = self.get_or_create(developer_id)
        if q.active_sandboxes >= q.max_sandboxes:
            return False, f"Sandbox limit reached ({q.max_sandboxes})"
        return True, "OK"

    def allocate(self, developer_id: str, memory_mb: int = 64) -> bool:
        ok, _ = self.can_create_sandbox(developer_id)
        if not ok: return False
        q = self._quotas[developer_id]
        if q.memory_used_mb + memory_mb > q.max_memory_mb:
            return False
        q.active_sandboxes += 1
        q.memory_used_mb += memory_mb
        return True

    def release(self, developer_id: str, memory_mb: int = 64) -> bool:
        q = self._quotas.get(developer_id)
        if not q or q.active_sandboxes <= 0: return False
        q.active_sandboxes -= 1
        q.memory_used_mb = max(0, q.memory_used_mb - memory_mb)
        return True

    def upgrade_tier(self, developer_id: str, tier: str) -> bool:
        if tier not in self.TIER_LIMITS: return False
        q = self.get_or_create(developer_id)
        limits = self.TIER_LIMITS[tier]
        q.tier = tier
        q.max_sandboxes = limits["sandboxes"]
        q.max_memory_mb = limits["memory"]
        q.max_cpu_seconds = limits["cpu"]
        return True

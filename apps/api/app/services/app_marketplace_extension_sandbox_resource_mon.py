"""Sandbox Resource Monitor — track CPU/memory/network per sandbox with limits.

Implements:
- Real-time resource sampling with rolling window
- Burst detection (sudden spikes above baseline)
- Auto-throttle when approaching limits
- OOM-kill simulation when hard limits exceeded
- Resource usage trend analysis
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque
import statistics


@dataclass
class ResourceSample:
    cpu_pct: float
    memory_mb: float
    network_kb: float
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class ResourceLimits:
    max_cpu_pct: float = 80.0
    max_memory_mb: float = 256.0
    max_network_kb_s: float = 1024.0
    burst_threshold: float = 2.0  # multiplier above baseline to detect burst


@dataclass
class SandboxResources:
    sandbox_id: str
    limits: ResourceLimits
    samples: deque = field(default_factory=lambda: deque(maxlen=120))  # 2 min at 1/s
    throttled: bool = False
    killed: bool = False
    kill_reason: str = ""


class SandboxResourceMonService:
    def __init__(self):
        self._sandboxes: dict[str, SandboxResources] = {}

    def register(self, sandbox_id: str, limits: ResourceLimits | None = None) -> SandboxResources:
        sr = SandboxResources(sandbox_id=sandbox_id, limits=limits or ResourceLimits())
        self._sandboxes[sandbox_id] = sr
        return sr

    def record_sample(self, sandbox_id: str, cpu_pct: float, memory_mb: float,
                      network_kb: float) -> dict:
        sr = self._sandboxes.get(sandbox_id)
        if not sr or sr.killed:
            return {"status": "dead", "reason": sr.kill_reason if sr else "not found"}

        sample = ResourceSample(cpu_pct=cpu_pct, memory_mb=memory_mb, network_kb=network_kb)
        sr.samples.append(sample)

        result = {"status": "ok", "alerts": []}

        # Hard limit check — OOM kill
        if memory_mb > sr.limits.max_memory_mb:
            sr.killed = True
            sr.kill_reason = f"OOM: {memory_mb:.0f}MB > {sr.limits.max_memory_mb:.0f}MB limit"
            result["status"] = "killed"
            result["reason"] = sr.kill_reason
            return result

        # Soft limit — throttle
        if cpu_pct > sr.limits.max_cpu_pct:
            sr.throttled = True
            result["alerts"].append(f"CPU throttled: {cpu_pct:.1f}% > {sr.limits.max_cpu_pct:.1f}%")
        elif sr.throttled and cpu_pct < sr.limits.max_cpu_pct * 0.7:
            sr.throttled = False  # release throttle at 70% of limit

        # Network limit
        if network_kb > sr.limits.max_network_kb_s:
            result["alerts"].append(f"Network limit: {network_kb:.0f}KB/s > {sr.limits.max_network_kb_s:.0f}KB/s")

        # Burst detection
        burst = self._detect_burst(sr, cpu_pct, "cpu")
        if burst:
            result["alerts"].append(burst)

        return result

    def _detect_burst(self, sr: SandboxResources, current: float, metric: str) -> str | None:
        if len(sr.samples) < 10:
            return None
        recent = list(sr.samples)[-10:]
        values = [s.cpu_pct for s in recent[:-1]]  # exclude current
        if not values:
            return None
        baseline = statistics.mean(values)
        if baseline > 0 and current > baseline * sr.limits.burst_threshold:
            return f"CPU burst detected: {current:.1f}% vs baseline {baseline:.1f}%"
        return None

    def get_stats(self, sandbox_id: str) -> dict | None:
        sr = self._sandboxes.get(sandbox_id)
        if not sr or not sr.samples:
            return None
        samples = list(sr.samples)
        cpu_values = [s.cpu_pct for s in samples]
        mem_values = [s.memory_mb for s in samples]
        return {
            "sandbox_id": sandbox_id,
            "alive": not sr.killed,
            "throttled": sr.throttled,
            "samples": len(samples),
            "cpu": {"current": cpu_values[-1], "avg": round(statistics.mean(cpu_values), 1),
                    "max": round(max(cpu_values), 1)},
            "memory": {"current": mem_values[-1], "avg": round(statistics.mean(mem_values), 1),
                       "max": round(max(mem_values), 1),
                       "limit": sr.limits.max_memory_mb},
        }

    def get_all_health(self) -> dict:
        alive = sum(1 for sr in self._sandboxes.values() if not sr.killed)
        throttled = sum(1 for sr in self._sandboxes.values() if sr.throttled)
        return {"total": len(self._sandboxes), "alive": alive,
                "killed": len(self._sandboxes) - alive, "throttled": throttled}

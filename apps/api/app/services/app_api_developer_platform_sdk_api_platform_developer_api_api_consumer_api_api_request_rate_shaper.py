"""API Consumer Request Rate Shaper — smooth request bursts over time."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RateShaperConfig:
    consumer_id: str
    target_rps: float  # desired steady-state requests per second
    burst_tolerance: float = 1.5  # allow 1.5x target briefly
    smoothing_window_s: int = 10

@dataclass
class ShapingDecision:
    allowed: bool
    delay_ms: int = 0  # suggested delay if shaped
    current_rps: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], RateShaperConfig] = {}
        self._windows: dict[tuple[str, str], list[float]] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def configure(self, installation_id: str, config: RateShaperConfig) -> RateShaperConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.target_rps <= 0: raise ValueError("target_rps must be > 0")
        if config.burst_tolerance < 1.0: raise ValueError("burst_tolerance must be >= 1.0")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def shape(self, installation_id: str, consumer_id: str) -> ShapingDecision:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return ShapingDecision(allowed=True)
        now = time.time()
        key = (installation_id, consumer_id)
        window = self._windows.setdefault(key, [])
        cutoff = now - config.smoothing_window_s
        window[:] = [t for t in window if t > cutoff]
        current_rps = len(window) / max(1, config.smoothing_window_s)
        max_rps = config.target_rps * config.burst_tolerance
        stats = self._stats.setdefault(installation_id, {"allowed": 0, "shaped": 0})
        if current_rps >= max_rps:
            delay = int((1 / config.target_rps) * 1000)
            stats["shaped"] += 1
            return ShapingDecision(allowed=False, delay_ms=delay, current_rps=round(current_rps, 2))
        window.append(now)
        stats["allowed"] += 1
        return ShapingDecision(allowed=True, current_rps=round(current_rps, 2))

    def shaping_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"allowed": 0, "shaped": 0})
        total = s["allowed"] + s["shaped"]
        return round((s["shaped"] / total) * 100, 1) if total > 0 else 0.0

    def list_configs(self, installation_id: str) -> list[RateShaperConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

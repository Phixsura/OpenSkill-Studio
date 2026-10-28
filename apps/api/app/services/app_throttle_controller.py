"""App Throttle Controller — adaptive throttling based on system load.

Manages adaptive request throttling:
- Configure load thresholds (low/medium/high/critical)
- Compute allowed throughput based on current load
- Gradual ramp-up/down of request limits
- Per-installation scoped controllers
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import structlog

log = structlog.get_logger()


class LoadLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThrottleConfig:
    """Configuration for adaptive throttling."""

    max_rps: float = 1000.0       # max requests/second at low load
    medium_pct: float = 75.0      # % of max at medium load
    high_pct: float = 50.0        # % of max at high load
    critical_pct: float = 10.0    # % of max at critical load
    load_low_threshold: float = 0.5
    load_medium_threshold: float = 0.7
    load_high_threshold: float = 0.85
    load_critical_threshold: float = 0.95


@dataclass
class ThrottleState:
    """Current throttle state."""

    load_level: LoadLevel
    current_load: float
    allowed_rps: float
    max_rps: float
    throttle_pct: float  # percentage of max being allowed


class AppThrottleController:
    """Adaptive request throttling based on system load."""

    def __init__(self, config: ThrottleConfig | None = None) -> None:
        self._config = config or ThrottleConfig()
        # installation_id → last known load
        self._load: dict[str, float] = {}

    def update_load(self, installation_id: str, load: float) -> ThrottleState:
        """Update the current load metric (0.0-1.0) and compute throttle state."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if load < 0:
            load = 0.0
        if load > 1:
            load = 1.0

        self._load[installation_id] = load
        return self._compute_state(installation_id, load)

    def get_state(self, installation_id: str) -> ThrottleState:
        """Get current throttle state."""
        load = self._load.get(installation_id, 0.0)
        return self._compute_state(installation_id, load)

    def should_allow(self, installation_id: str, current_rps: float) -> bool:
        """Check if a request should be allowed based on current throttle."""
        state = self.get_state(installation_id)
        return current_rps <= state.allowed_rps

    def get_allowed_rps(self, installation_id: str) -> float:
        """Get the currently allowed requests per second."""
        return self.get_state(installation_id).allowed_rps

    def reset_load(self, installation_id: str) -> None:
        """Reset load to zero."""
        self._load[installation_id] = 0.0

    def _compute_state(self, installation_id: str, load: float) -> ThrottleState:
        cfg = self._config

        if load >= cfg.load_critical_threshold:
            level = LoadLevel.CRITICAL
            pct = cfg.critical_pct
        elif load >= cfg.load_high_threshold:
            level = LoadLevel.HIGH
            pct = cfg.high_pct
        elif load >= cfg.load_medium_threshold:
            level = LoadLevel.MEDIUM
            pct = cfg.medium_pct
        else:
            level = LoadLevel.LOW
            pct = 100.0

        allowed = cfg.max_rps * (pct / 100.0)

        return ThrottleState(
            load_level=level,
            current_load=load,
            allowed_rps=round(allowed, 2),
            max_rps=cfg.max_rps,
            throttle_pct=round(pct, 2),
        )

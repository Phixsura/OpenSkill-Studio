"""Consumer API Request Throttle — adaptive request throttling with backpressure."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ThrottleConfig:
    consumer_id: str
    base_rate: int = 100  # requests per window
    window_seconds: float = 60.0
    backpressure_threshold: float = 0.8  # 80% utilization triggers backpressure
    adaptive: bool = True


@dataclass
class ThrottleState:
    current_count: int = 0
    window_start: float = 0.0
    throttled_count: int = 0
    backpressure_active: bool = False
    effective_rate: int = 100


@dataclass
class RequestThrottle:
    """Adaptive request throttling with backpressure signaling."""

    _configs: dict[str, ThrottleConfig] = field(default_factory=dict)
    _states: dict[str, ThrottleState] = field(default_factory=dict)

    def configure(self, config: ThrottleConfig) -> dict:
        if config.base_rate < 1:
            raise ValueError("base_rate must be positive")
        self._configs[config.consumer_id] = config
        self._states.setdefault(config.consumer_id, ThrottleState(effective_rate=config.base_rate))
        return {"consumer_id": config.consumer_id, "base_rate": config.base_rate}

    def check(self, consumer_id: str, current_time: float = 0.0) -> dict:
        config = self._configs.get(consumer_id)
        if not config:
            return {"allowed": True, "reason": "no_config"}
        state = self._states[consumer_id]
        # Reset window if expired
        if current_time - state.window_start >= config.window_seconds:
            state.current_count = 0
            state.window_start = current_time
            state.backpressure_active = False
            if config.adaptive:
                state.effective_rate = config.base_rate

        utilization = state.current_count / state.effective_rate if state.effective_rate > 0 else 1.0

        # Backpressure check
        if utilization >= config.backpressure_threshold and config.adaptive:
            state.backpressure_active = True
            # Reduce effective rate by 20%
            state.effective_rate = max(1, int(state.effective_rate * 0.8))

        if state.current_count >= state.effective_rate:
            state.throttled_count += 1
            remaining_window = config.window_seconds - (current_time - state.window_start)
            return {
                "allowed": False, "reason": "throttled",
                "retry_after_seconds": round(max(0, remaining_window), 2),
                "backpressure": state.backpressure_active,
            }

        state.current_count += 1
        remaining = state.effective_rate - state.current_count
        return {
            "allowed": True,
            "remaining": remaining,
            "effective_rate": state.effective_rate,
            "backpressure": state.backpressure_active,
            "utilization_pct": round(utilization * 100, 1),
        }

    def get_status(self, consumer_id: str) -> dict:
        config = self._configs.get(consumer_id)
        state = self._states.get(consumer_id)
        if not config or not state:
            return {"consumer_id": consumer_id, "status": "unconfigured"}
        return {
            "consumer_id": consumer_id,
            "base_rate": config.base_rate,
            "effective_rate": state.effective_rate,
            "current_count": state.current_count,
            "throttled_count": state.throttled_count,
            "backpressure": state.backpressure_active,
            "adaptive": config.adaptive,
        }

    def reset(self, consumer_id: str) -> dict:
        config = self._configs.get(consumer_id)
        if not config:
            return {"reset": False}
        self._states[consumer_id] = ThrottleState(effective_rate=config.base_rate)
        return {"reset": True}

    def list_consumers(self) -> list[dict]:
        return [self.get_status(cid) for cid in sorted(self._configs)]

    def get_stats(self) -> dict:
        states = list(self._states.values())
        return {
            "total_consumers": len(self._configs),
            "total_throttled": sum(s.throttled_count for s in states),
            "backpressure_active": sum(1 for s in states if s.backpressure_active),
        }

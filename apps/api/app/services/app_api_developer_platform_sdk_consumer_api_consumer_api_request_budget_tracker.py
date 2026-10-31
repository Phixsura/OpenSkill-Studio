"""Consumer API Request Budget Tracker — track daily/monthly request budgets."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class BudgetConfig:
    consumer_id: str
    daily_budget: int = 10000
    monthly_budget: int = 300000
    alert_threshold_pct: float = 80.0
    auto_block: bool = False

@dataclass
class BudgetState:
    consumer_id: str
    daily_used: int
    daily_budget: int
    monthly_used: int
    monthly_budget: int
    daily_pct: float
    monthly_pct: float
    alert_triggered: bool
    blocked: bool

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], BudgetConfig] = {}
        self._daily: dict[tuple[str, str, str], int] = {}  # (inst, consumer, date_str) -> count
        self._monthly: dict[tuple[str, str, str], int] = {}  # (inst, consumer, month_str) -> count

    def configure(self, installation_id: str, config: BudgetConfig) -> BudgetConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.daily_budget < 1:
            raise ValueError("daily_budget must be positive")
        if config.monthly_budget < config.daily_budget:
            raise ValueError("monthly_budget must be >= daily_budget")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def consume(self, installation_id: str, consumer_id: str, now: datetime, count: int = 1) -> BudgetState:
        if count < 0:
            raise ValueError("count must be non-negative")
        config = self._configs.get((installation_id, consumer_id), BudgetConfig(consumer_id=consumer_id))
        date_str = now.strftime("%Y-%m-%d")
        month_str = now.strftime("%Y-%m")
        dk = (installation_id, consumer_id, date_str)
        mk = (installation_id, consumer_id, month_str)
        self._daily[dk] = self._daily.get(dk, 0) + count
        self._monthly[mk] = self._monthly.get(mk, 0) + count
        daily_used = self._daily[dk]
        monthly_used = self._monthly[mk]
        daily_pct = round(daily_used / max(config.daily_budget, 1) * 100, 1)
        monthly_pct = round(monthly_used / max(config.monthly_budget, 1) * 100, 1)
        alert = daily_pct >= config.alert_threshold_pct or monthly_pct >= config.alert_threshold_pct
        blocked = config.auto_block and (daily_used > config.daily_budget or monthly_used > config.monthly_budget)
        return BudgetState(consumer_id=consumer_id, daily_used=daily_used, daily_budget=config.daily_budget, monthly_used=monthly_used, monthly_budget=config.monthly_budget, daily_pct=daily_pct, monthly_pct=monthly_pct, alert_triggered=alert, blocked=blocked)

    def get_state(self, installation_id: str, consumer_id: str, now: datetime) -> BudgetState:
        config = self._configs.get((installation_id, consumer_id), BudgetConfig(consumer_id=consumer_id))
        date_str = now.strftime("%Y-%m-%d")
        month_str = now.strftime("%Y-%m")
        daily = self._daily.get((installation_id, consumer_id, date_str), 0)
        monthly = self._monthly.get((installation_id, consumer_id, month_str), 0)
        daily_pct = round(daily / max(config.daily_budget, 1) * 100, 1)
        monthly_pct = round(monthly / max(config.monthly_budget, 1) * 100, 1)
        alert = daily_pct >= config.alert_threshold_pct or monthly_pct >= config.alert_threshold_pct
        blocked = config.auto_block and (daily > config.daily_budget or monthly > config.monthly_budget)
        return BudgetState(consumer_id=consumer_id, daily_used=daily, daily_budget=config.daily_budget, monthly_used=monthly, monthly_budget=config.monthly_budget, daily_pct=daily_pct, monthly_pct=monthly_pct, alert_triggered=alert, blocked=blocked)

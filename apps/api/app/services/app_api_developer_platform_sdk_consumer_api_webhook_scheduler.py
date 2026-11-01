"""Consumer API Webhook Scheduler — scheduled webhook deliveries with cron."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

FREQUENCIES = ("once", "hourly", "daily", "weekly", "monthly", "cron")


@dataclass
class ScheduledWebhook:
    schedule_id: str
    webhook_url: str
    event_type: str
    frequency: str
    cron_expression: str = ""
    payload_template: dict = field(default_factory=dict)
    enabled: bool = True
    execution_count: int = 0
    last_executed: str = ""
    next_execution: str = ""


@dataclass
class WebhookScheduler:
    """Schedule recurring webhook deliveries."""

    _schedules: dict[str, ScheduledWebhook] = field(default_factory=dict)
    _execution_log: list[dict] = field(default_factory=list)

    def create_schedule(self, schedule: ScheduledWebhook) -> dict:
        if schedule.schedule_id in self._schedules:
            raise ValueError(f"Schedule {schedule.schedule_id} already exists")
        if schedule.frequency not in FREQUENCIES:
            raise ValueError(f"Invalid frequency: {schedule.frequency}")
        if schedule.frequency == "cron" and not schedule.cron_expression:
            raise ValueError("cron_expression required for cron frequency")
        if not schedule.webhook_url.startswith("http"):
            raise ValueError("webhook_url must start with http")
        self._schedules[schedule.schedule_id] = schedule
        logger.info("webhook_scheduled", schedule_id=schedule.schedule_id)
        return {"schedule_id": schedule.schedule_id, "frequency": schedule.frequency}

    def execute(self, schedule_id: str, timestamp: str = "") -> dict:
        sched = self._schedules.get(schedule_id)
        if not sched:
            raise ValueError(f"Schedule {schedule_id} not found")
        if not sched.enabled:
            return {"executed": False, "reason": "disabled"}
        sched.execution_count += 1
        sched.last_executed = timestamp
        self._execution_log.append({
            "schedule_id": schedule_id, "timestamp": timestamp,
            "execution_number": sched.execution_count,
        })
        if sched.frequency == "once":
            sched.enabled = False
        logger.info("webhook_executed", schedule_id=schedule_id)
        return {"executed": True, "execution_count": sched.execution_count}

    def toggle(self, schedule_id: str, enabled: bool) -> dict:
        sched = self._schedules.get(schedule_id)
        if not sched:
            raise ValueError(f"Schedule {schedule_id} not found")
        sched.enabled = enabled
        return {"schedule_id": schedule_id, "enabled": enabled}

    def delete(self, schedule_id: str) -> dict:
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return {"deleted": True}
        return {"deleted": False}

    def get_due(self) -> list[dict]:
        return [
            {"schedule_id": s.schedule_id, "frequency": s.frequency,
             "webhook_url": s.webhook_url, "event_type": s.event_type}
            for s in self._schedules.values() if s.enabled
        ]

    def list_schedules(self) -> list[dict]:
        return [
            {"schedule_id": s.schedule_id, "frequency": s.frequency,
             "event_type": s.event_type, "enabled": s.enabled,
             "executions": s.execution_count}
            for s in self._schedules.values()
        ]

    def get_execution_log(self, schedule_id: str | None = None, limit: int = 20) -> list[dict]:
        log = self._execution_log
        if schedule_id:
            log = [e for e in log if e["schedule_id"] == schedule_id]
        return log[-limit:]

    def get_stats(self) -> dict:
        schedules = list(self._schedules.values())
        return {
            "total_schedules": len(schedules),
            "enabled": sum(1 for s in schedules if s.enabled),
            "disabled": sum(1 for s in schedules if not s.enabled),
            "total_executions": len(self._execution_log),
        }

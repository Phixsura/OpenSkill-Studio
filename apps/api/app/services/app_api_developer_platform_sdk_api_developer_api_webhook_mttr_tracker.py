"""App API Developer Webhook MTTR Tracker — mean time to recover from webhook failures."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RecoveryRecord:
    incident_id: str
    destination: str
    failed_at: float
    recovered_at: float | None = None
    recovery_time_seconds: float | None = None

class AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTracker:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], RecoveryRecord] = {}

    def record_failure(self, installation_id: str, incident_id: str, destination: str) -> RecoveryRecord:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, incident_id)
        r = RecoveryRecord(incident_id=incident_id, destination=destination, failed_at=time.time())
        self._records[key] = r
        return r

    def record_recovery(self, installation_id: str, incident_id: str) -> RecoveryRecord:
        key = (installation_id, incident_id)
        r = self._records.get(key)
        if r is None: raise KeyError(f"Incident {incident_id} not found")
        r.recovered_at = time.time()
        r.recovery_time_seconds = round(r.recovered_at - r.failed_at, 1)
        return r

    def mttr_seconds(self, installation_id: str) -> float:
        recovered = [r for (inst, _), r in self._records.items() if inst == installation_id and r.recovery_time_seconds is not None]
        if not recovered: return 0.0
        return round(sum(r.recovery_time_seconds for r in recovered) / len(recovered), 1)

    def open_incidents(self, installation_id: str) -> list[RecoveryRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id and r.recovered_at is None]

    def total_incidents(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._records if inst == installation_id)

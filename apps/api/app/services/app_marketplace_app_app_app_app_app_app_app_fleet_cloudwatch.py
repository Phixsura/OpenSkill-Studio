"""Fleet CloudWatch — track AWS monitoring integration."""
from __future__ import annotations
def fleet_cloudwatch_status(alarms: list[dict]) -> dict:
    ok = [a for a in alarms if a.get("state") == "OK"]
    alarm = [a for a in alarms if a.get("state") == "ALARM"]
    insufficient = [a for a in alarms if a.get("state") == "INSUFFICIENT_DATA"]
    return {"total": len(alarms), "ok": len(ok), "alarm": len(alarm),
            "insufficient": len(insufficient), "calm": len(alarm) == 0}

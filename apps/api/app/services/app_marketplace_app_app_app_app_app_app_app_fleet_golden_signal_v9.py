"""Fleet Golden Signal v9 — track the four golden signals of monitoring."""
from __future__ import annotations
def fleet_golden_signal_v9(services: list[dict]) -> dict:
    latency_ok = [s for s in services if s.get("latency_ok", True)]
    traffic_ok = [s for s in services if s.get("traffic_ok", True)]
    errors_ok = [s for s in services if s.get("errors_ok", True)]
    saturation_ok = [s for s in services if s.get("saturation_ok", True)]
    return {"services": len(services), "latency_ok": len(latency_ok), "traffic_ok": len(traffic_ok),
            "errors_ok": len(errors_ok), "saturation_ok": len(saturation_ok),
            "healthy": all(len(x) == len(services) for x in [latency_ok, traffic_ok, errors_ok, saturation_ok])}

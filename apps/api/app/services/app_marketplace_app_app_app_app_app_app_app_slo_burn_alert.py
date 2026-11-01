"""SLO burn alert — multi-window burn rate alerting."""
from __future__ import annotations


def calculate_burn_alert(slo_target: float, error_budget_consumed_pct: float,
                           elapsed_pct: float) -> dict:
    burn_rate = round(error_budget_consumed_pct / max(elapsed_pct, 0.1), 2)
    # Multi-window: 1h and 5m burn rates
    alert_level = "page" if burn_rate > 14.4 else "ticket" if burn_rate > 6 else "log" if burn_rate > 3 else "none"
    time_to_exhaust_hours = round((100 - error_budget_consumed_pct) / max(burn_rate * elapsed_pct / 100, 0.01), 1) if burn_rate > 0 else 999
    return {"slo_target": slo_target, "burn_rate": burn_rate,
            "budget_consumed_pct": error_budget_consumed_pct,
            "elapsed_pct": elapsed_pct, "alert_level": alert_level,
            "time_to_exhaust_hours": max(0, time_to_exhaust_hours),
            "critical": alert_level == "page"}


def summarize_burn_alerts(alerts: list[dict]) -> dict:
    paging = sum(1 for a in alerts if a["alert_level"] == "page")
    ticketing = sum(1 for a in alerts if a["alert_level"] == "ticket")
    return {"total": len(alerts), "paging": paging, "ticketing": ticketing,
            "silent": len(alerts) - paging - ticketing,
            "any_critical": paging > 0}

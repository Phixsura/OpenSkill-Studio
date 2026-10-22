"""Disaster recovery — DR planning and failover management."""

from datetime import datetime, timezone


def create_dr_plan(*, app_id: str, rpo_minutes: int, rto_minutes: int,
                     backup_regions: list[str]) -> dict:
    if rpo_minutes < 1:
        return {"error": "RPO must be at least 1 minute"}
    if rto_minutes < 1:
        return {"error": "RTO must be at least 1 minute"}
    return {"app_id": app_id, "rpo_minutes": rpo_minutes, "rto_minutes": rto_minutes,
            "backup_regions": backup_regions, "status": "active", "error": None}


def simulate_failover(*, primary_region: str, backup_region: str, data_lag_minutes: int,
                        rpo_minutes: int) -> dict:
    within_rpo = data_lag_minutes <= rpo_minutes
    return {"from_region": primary_region, "to_region": backup_region,
            "data_lag_minutes": data_lag_minutes, "within_rpo": within_rpo,
            "data_loss_risk": "none" if within_rpo else "possible"}


def get_dr_readiness(*, backups_current: bool, failover_tested: bool,
                       monitoring_active: bool) -> dict:
    checks = {"backups": backups_current, "failover_tested": failover_tested, "monitoring": monitoring_active}
    score = sum(1 for v in checks.values() if v)
    return {"ready": score == 3, "score": f"{score}/3", "checks": checks}

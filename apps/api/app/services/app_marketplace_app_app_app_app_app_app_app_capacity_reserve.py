"""Capacity reservation manager — reserve resources for critical workloads."""
from __future__ import annotations


def create_reservation(name: str, resource_type: str, amount: float,
                         priority: str = "normal") -> dict:
    return {"name": name, "type": resource_type, "amount": amount,
            "priority": priority, "status": "active", "utilized": 0}


def check_utilization(reservations: list[dict]) -> dict:
    total_reserved = sum(r["amount"] for r in reservations)
    total_utilized = sum(r.get("utilized", 0) for r in reservations)
    underutilized = [r for r in reservations if r.get("utilized", 0) < r["amount"] * 0.3]
    return {"total_reserved": total_reserved, "total_utilized": round(total_utilized, 1),
            "utilization_pct": round(total_utilized / max(total_reserved, 0.01) * 100),
            "underutilized": [r["name"] for r in underutilized],
            "waste_count": len(underutilized)}

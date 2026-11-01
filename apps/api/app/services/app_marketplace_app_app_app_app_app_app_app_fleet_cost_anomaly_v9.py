"""Fleet Cost Anomaly v9 — detect unusual spending patterns."""
from __future__ import annotations
def fleet_cost_anomaly_v9(bills: list[dict]) -> dict:
    amounts = [b.get("amount", 0) for b in bills]
    avg = sum(amounts) / len(amounts) if amounts else 0
    anomalies = [b for b in bills if b.get("amount", 0) > avg * 2]
    return {"total_bills": len(bills), "avg_amount": round(avg, 2),
            "anomalies": len(anomalies), "total_spend": sum(amounts),
            "healthy": len(anomalies) == 0}

"""Fleet Cloud Native v9 — track cloud-native maturity across workloads."""
from __future__ import annotations
def fleet_cloud_native_v9(workloads: list[dict]) -> dict:
    containerized = [w for w in workloads if w.get("containerized")]
    serverless = [w for w in workloads if w.get("serverless")]
    maturity = sum(w.get("maturity_score", 0) for w in workloads) / len(workloads) if workloads else 0
    return {"workloads": len(workloads), "containerized": len(containerized),
            "serverless": len(serverless), "avg_maturity": round(maturity, 1),
            "healthy": maturity > 3}

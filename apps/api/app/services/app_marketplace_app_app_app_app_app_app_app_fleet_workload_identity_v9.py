"""Fleet Workload Identity v9 — track workload identity federation."""
from __future__ import annotations
def fleet_workload_identity_v9(workloads: list[dict]) -> dict:
    federated = [w for w in workloads if w.get("identity_federated")]
    sa_bound = [w for w in workloads if w.get("service_account_bound")]
    token_audience = len({w.get("audience") for w in workloads if w.get("audience")})
    return {"workloads": len(workloads), "federated": len(federated), "sa_bound": len(sa_bound),
            "unique_audiences": token_audience, "healthy": len(federated) == len(workloads)}

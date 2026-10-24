"""Fleet Kubeflow — track ML platform on Kubernetes."""
from __future__ import annotations
def fleet_kubeflow_status(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("healthy", True)]
    pipelines = sum(c.get("pipelines", 0) for c in clusters)
    notebooks = sum(c.get("notebooks", 0) for c in clusters)
    experiments = sum(c.get("experiments", 0) for c in clusters)
    return {"clusters": len(clusters), "healthy": len(healthy), "pipelines": pipelines,
            "notebooks": notebooks, "experiments": experiments}

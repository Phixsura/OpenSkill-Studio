"""Platform feature catalog — registry of all platform capabilities."""
from __future__ import annotations

FEATURES = {
    "sdk": {"name": "Extension SDK", "status": "ga", "module": "core"},
    "sandbox": {"name": "Sandboxed Apps", "status": "ga", "module": "core"},
    "marketplace": {"name": "Connector Marketplace", "status": "ga", "module": "core"},
    "automation": {"name": "Automation API", "status": "ga", "module": "core"},
    "webhooks": {"name": "Webhooks", "status": "ga", "module": "integration"},
    "oauth": {"name": "OAuth 2.0", "status": "ga", "module": "security"},
    "rbac": {"name": "Role-Based Access", "status": "ga", "module": "security"},
    "observability": {"name": "Full Observability", "status": "ga", "module": "ops"},
    "cicd": {"name": "CI/CD Pipelines", "status": "ga", "module": "ops"},
    "multi_region": {"name": "Multi-Region Deploy", "status": "beta", "module": "infra"},
}


def list_features(status: str | None = None, module: str | None = None) -> dict:
    items = list(FEATURES.values())
    if status:
        items = [f for f in items if f["status"] == status]
    if module:
        items = [f for f in items if f["module"] == module]
    modules = sorted({f["module"] for f in items})
    return {"features": items, "total": len(items), "modules": modules}


def feature_summary() -> dict:
    ga = sum(1 for f in FEATURES.values() if f["status"] == "ga")
    beta = sum(1 for f in FEATURES.values() if f["status"] == "beta")
    return {"total": len(FEATURES), "ga": ga, "beta": beta,
            "ga_pct": round(ga / len(FEATURES) * 100)}

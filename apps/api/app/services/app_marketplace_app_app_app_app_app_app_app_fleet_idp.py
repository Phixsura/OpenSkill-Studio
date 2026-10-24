"""Fleet IDP — internal developer portal metrics."""
from __future__ import annotations
def fleet_idp_metrics(metrics: dict) -> dict:
    templates = metrics.get("service_templates", 0)
    scaffolds = metrics.get("scaffolds_used_30d", 0)
    docs_pages = metrics.get("docs_pages", 0)
    return {"templates": templates, "scaffolds_30d": scaffolds, "docs_pages": docs_pages,
            "adoption_score": round((templates * 5 + scaffolds + docs_pages / 10) / 3, 1)}

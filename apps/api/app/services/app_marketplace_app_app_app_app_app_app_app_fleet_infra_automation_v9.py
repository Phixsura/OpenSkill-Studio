"""Fleet Infra Automation v9 — track infrastructure automation coverage."""
from __future__ import annotations
def fleet_infra_automation_v9(resources: list[dict]) -> dict:
    automated = [r for r in resources if r.get("automated")]
    manual = [r for r in resources if not r.get("automated")]
    iac_coverage = round(len(automated) / len(resources) * 100, 1) if resources else 0
    return {"resources": len(resources), "automated": len(automated), "manual": len(manual),
            "iac_coverage_pct": iac_coverage, "healthy": iac_coverage > 95}

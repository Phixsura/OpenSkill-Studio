"""Fleet Azure SWA — track static web app hosting."""
from __future__ import annotations
def fleet_azure_swa_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    apis = sum(a.get("api_functions", 0) for a in apps)
    custom_domains = sum(a.get("custom_domains", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "api_functions": apis,
            "custom_domains": custom_domains, "all_deployed": len(deployed) == len(apps)}

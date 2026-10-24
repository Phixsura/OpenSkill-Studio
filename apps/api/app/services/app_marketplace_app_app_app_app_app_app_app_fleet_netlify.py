"""Fleet Netlify — track web platform health."""
from __future__ import annotations
def fleet_netlify_status(sites: list[dict]) -> dict:
    published = [s for s in sites if s.get("published", True)]
    deploys_24h = sum(s.get("deploys_24h", 0) for s in sites)
    functions = sum(s.get("functions", 0) for s in sites)
    return {"sites": len(sites), "published": len(published), "deploys_24h": deploys_24h,
            "functions": functions, "all_published": len(published) == len(sites)}

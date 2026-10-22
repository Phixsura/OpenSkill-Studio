"""Multi-region — manage app deployments across geographic regions."""

AVAILABLE_REGIONS = {
    "us-east-1": {"name": "US East", "location": "Virginia"},
    "us-west-2": {"name": "US West", "location": "Oregon"},
    "eu-west-1": {"name": "Europe", "location": "Ireland"},
    "ap-northeast-1": {"name": "Asia Pacific", "location": "Tokyo"},
}


def list_regions() -> list[dict]:
    return [{"id": k, **v} for k, v in AVAILABLE_REGIONS.items()]


def deploy_to_region(*, app_id: str, version_id: str, region: str) -> dict:
    if region not in AVAILABLE_REGIONS:
        return {"error": f"Unknown region: {region}"}
    return {"app_id": app_id, "version_id": version_id, "region": region,
            "region_name": AVAILABLE_REGIONS[region]["name"], "status": "deploying", "error": None}


def get_region_health(*, deployments: list[dict]) -> dict:
    healthy = sum(1 for d in deployments if d.get("status") == "healthy")
    return {"total_regions": len(deployments), "healthy": healthy,
            "global_status": "healthy" if healthy == len(deployments) else "partial" if healthy > 0 else "down"}

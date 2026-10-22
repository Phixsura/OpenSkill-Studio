"""API versioning — manage multiple API versions for backward compatibility."""


def create_api_version(*, app_id: str, version: str, endpoints: list[dict],
                         deprecated_from: str | None = None) -> dict:
    if not version.startswith("v"):
        return {"error": "Version must start with 'v' (e.g., v1, v2)"}
    return {"app_id": app_id, "version": version, "endpoint_count": len(endpoints),
            "endpoints": endpoints, "deprecated": deprecated_from is not None,
            "deprecated_from": deprecated_from, "error": None}


def route_to_version(*, requested_version: str, available: list[str], default: str = "v1") -> dict:
    if requested_version in available:
        return {"version": requested_version, "fallback": False}
    return {"version": default, "fallback": True, "warning": f"Version {requested_version} not found, using {default}"}


def build_version_matrix(*, versions: list[dict]) -> dict:
    all_paths = set()
    for v in versions:
        for ep in v.get("endpoints", []):
            all_paths.add(ep.get("path", ""))
    matrix = []
    for path in sorted(all_paths):
        row = {"path": path}
        for v in versions:
            row[v["version"]] = any(ep.get("path") == path for ep in v.get("endpoints", []))
        matrix.append(row)
    return {"matrix": matrix, "versions": [v["version"] for v in versions]}

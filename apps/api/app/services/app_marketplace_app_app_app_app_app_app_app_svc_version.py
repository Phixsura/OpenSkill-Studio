"""Service version tracker — track deployed versions across environments."""
from __future__ import annotations


def track_versions(deployments: list[dict]) -> dict:
    by_service: dict[str, dict[str, str]] = {}
    for d in deployments:
        svc = d["service"]
        env = d["env"]
        version = d["version"]
        by_service.setdefault(svc, {})[env] = version
    inconsistent = []
    for svc, envs in by_service.items():
        versions = set(envs.values())
        if len(versions) > 1:
            inconsistent.append({"service": svc, "versions": dict(envs)})
    return {"services": by_service, "total_services": len(by_service),
            "inconsistent": inconsistent,
            "all_consistent": len(inconsistent) == 0}


def version_matrix(services: dict[str, dict[str, str]], envs: list[str]) -> list[dict]:
    rows = []
    for svc, versions in sorted(services.items()):
        row = {"service": svc}
        for env in envs:
            row[env] = versions.get(env, "-")
        rows.append(row)
    return rows

"""Deployment changelog builder — build changelogs from deployments."""
from __future__ import annotations


def build_deploy_changelog(deployments: list[dict]) -> dict:
    entries = []
    for d in deployments:
        changes = d.get("changes", [])
        features = [c for c in changes if c.get("type") == "feat"]
        fixes = [c for c in changes if c.get("type") == "fix"]
        entries.append({"version": d["version"], "env": d.get("env", "prod"),
                        "features": len(features), "fixes": len(fixes),
                        "total_changes": len(changes),
                        "deployer": d.get("deployer", "ci")})
    total_features = sum(e["features"] for e in entries)
    total_fixes = sum(e["fixes"] for e in entries)
    return {"entries": entries, "total_deployments": len(entries),
            "total_features": total_features, "total_fixes": total_fixes}

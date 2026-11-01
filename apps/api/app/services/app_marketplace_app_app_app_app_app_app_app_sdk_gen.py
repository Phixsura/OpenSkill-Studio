"""API client SDK generator — generate SDK metadata from API specs."""
from __future__ import annotations


def generate_sdk_metadata(endpoints: list[dict], sdk_name: str, version: str) -> dict:
    methods = []
    for ep in endpoints:
        method_name = ep["path"].strip("/").replace("/", "_").replace("{", "").replace("}", "")
        methods.append({"name": method_name, "http_method": ep["method"],
                        "path": ep["path"], "params": ep.get("params", [])})
    return {"sdk_name": sdk_name, "version": version, "methods": methods,
            "total_methods": len(methods), "language": "typescript"}


def sdk_coverage(endpoints: list[dict], sdk_methods: list[str]) -> dict:
    ep_set = {f"{e['method']} {e['path']}" for e in endpoints}
    covered = sum(1 for m in sdk_methods if m in ep_set)
    return {"total_endpoints": len(ep_set), "covered": covered,
            "uncovered": len(ep_set) - covered,
            "coverage_pct": round(covered / max(len(ep_set), 1) * 100, 1)}

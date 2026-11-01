"""Fleet AI API Versioner — track API version management and migration."""
from __future__ import annotations
def fleet_ai_api_versioner(versioners: list[dict]) -> dict:
    active = [v for v in versioners if v.get("active", True)]
    apis = sum(v.get("apis", 0) for v in versioners)
    versions = sum(v.get("versions", 0) for v in versioners)
    deprecated = sum(v.get("deprecated", 0) for v in versioners)
    return {"versioners": len(versioners), "active": len(active), "apis": apis,
            "versions": versions, "deprecated": deprecated, "managed": apis > 0}

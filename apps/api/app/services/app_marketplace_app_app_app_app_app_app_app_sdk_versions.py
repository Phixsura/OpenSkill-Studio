"""SDK version checker — track SDK versions across languages."""
from __future__ import annotations

SDK_REGISTRY = {
    "typescript": {"package": "@openskill/sdk", "latest": "3.5.0", "min_supported": "3.0.0"},
    "python": {"package": "openskill-sdk", "latest": "3.5.0", "min_supported": "3.0.0"},
    "go": {"package": "github.com/openskill/sdk-go", "latest": "3.5.0", "min_supported": "3.0.0"},
    "java": {"package": "io.openskill:sdk", "latest": "3.5.0", "min_supported": "3.0.0"},
    "ruby": {"package": "openskill-sdk", "latest": "3.5.0", "min_supported": "3.0.0"},
}


def check_sdk_version(language: str, version: str) -> dict:
    sdk = SDK_REGISTRY.get(language)
    if not sdk:
        return {"error": f"Unknown SDK: {language}"}
    up_to_date = version == sdk["latest"]
    supported = version >= sdk["min_supported"]
    return {"language": language, "current": version, "latest": sdk["latest"],
            "up_to_date": up_to_date, "supported": supported,
            "action": "none" if up_to_date else "update_recommended" if supported else "update_required"}


def list_sdks() -> list[dict]:
    return [{"language": k, "package": v["package"], "latest": v["latest"]}
            for k, v in SDK_REGISTRY.items()]

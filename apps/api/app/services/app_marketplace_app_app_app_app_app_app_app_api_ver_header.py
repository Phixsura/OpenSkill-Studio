"""API versioning header — parse and validate API version from request headers."""
from __future__ import annotations

SUPPORTED_VERSIONS = ["v1", "v2", "v3"]
LATEST_VERSION = "v3"
DEPRECATED_VERSIONS = ["v1"]


def parse_api_version(*, accept_header: str = "", url_version: str = "") -> dict:
    version = url_version or _extract_from_header(accept_header) or LATEST_VERSION
    if version not in SUPPORTED_VERSIONS:
        return {"version": LATEST_VERSION, "valid": False, "error": f"Unknown version: {version}",
                "fallback": True}
    deprecated = version in DEPRECATED_VERSIONS
    return {"version": version, "valid": True, "deprecated": deprecated,
            "latest": version == LATEST_VERSION, "fallback": False,
            "warning": f"{version} is deprecated — migrate to {LATEST_VERSION}" if deprecated else None}


def _extract_from_header(header: str) -> str:
    if "version=" in header:
        for part in header.split(";"):
            if "version=" in part:
                return part.split("=")[-1].strip()
    return ""


def list_versions() -> list[dict]:
    return [{"version": v, "latest": v == LATEST_VERSION,
             "deprecated": v in DEPRECATED_VERSIONS} for v in SUPPORTED_VERSIONS]

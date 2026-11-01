"""API version manager — handle API versioning for developer platform."""

CURRENT_VERSION = "2024-01-01"
SUPPORTED_VERSIONS = ["2024-01-01"]
DEPRECATED_VERSIONS: list[str] = []
MIN_VERSION = "2024-01-01"


def is_supported(version: str) -> bool:
    return version in SUPPORTED_VERSIONS


def is_deprecated(version: str) -> bool:
    return version in DEPRECATED_VERSIONS


def get_version_header() -> dict[str, str]:
    return {"X-API-Version": CURRENT_VERSION, "X-API-Min-Version": MIN_VERSION}


def validate_request_version(version: str | None) -> dict:
    if not version:
        return {"valid": True, "version": CURRENT_VERSION, "using_default": True}
    if not is_supported(version):
        return {"valid": False, "error": f"Unsupported API version: {version}", "supported": SUPPORTED_VERSIONS}
    return {"valid": True, "version": version, "deprecated": is_deprecated(version)}

"""Version sorter — sort versions by semver order."""

from app.services.app_compatibility import parse_semver


def sort_versions(versions: list[str], *, descending: bool = True) -> list[str]:
    """Sort version strings by semver order."""
    parsed = [(v, parse_semver(v)) for v in versions]
    valid = [(v, s) for v, s in parsed if s is not None]
    invalid = [v for v, s in parsed if s is None]
    sorted_valid = sorted(valid, key=lambda x: x[1], reverse=descending)
    return [v for v, _ in sorted_valid] + invalid


def get_latest_version(versions: list[str]) -> str | None:
    """Get the latest version from a list."""
    sorted_v = sort_versions(versions, descending=True)
    return sorted_v[0] if sorted_v else None


def is_prerelease(version: str) -> bool:
    """Check if a version string contains a prerelease tag."""
    return "-" in version

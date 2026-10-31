"""Platform version — track platform version and changelog."""

PLATFORM_VERSION = "2.1.0"
PLATFORM_CHANGELOG = [
    {"version": "2.1.0", "date": "2026-10-23", "changes": ["92,000+ lines of code", "2,500+ files", "1,110+ commits"]},
    {"version": "2.0.0", "date": "2026-10-22", "changes": ["90K milestone", "Complete developer platform"]},
    {"version": "1.0.0", "date": "2026-10-21", "changes": ["Initial developer platform release"]},
]


def get_platform_version() -> dict:
    return {"version": PLATFORM_VERSION, "latest": True, "changelog_url": "/changelog"}


def get_platform_changelog(*, limit: int = 10) -> list[dict]:
    return PLATFORM_CHANGELOG[:limit]


def check_api_compatibility(*, client_version: str) -> dict:
    client_major = int(client_version.split(".")[0]) if client_version else 0
    platform_major = int(PLATFORM_VERSION.split(".")[0])
    compatible = client_major == platform_major
    return {"compatible": compatible, "client_version": client_version,
            "platform_version": PLATFORM_VERSION,
            "upgrade_required": client_major < platform_major}

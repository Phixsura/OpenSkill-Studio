"""Changelog page builder — compile changelog page with all versions."""

def build_changelog_page(*, app_name: str, versions: list[dict]) -> dict:
    return {"app_name": app_name, "versions": versions, "version_count": len(versions)}

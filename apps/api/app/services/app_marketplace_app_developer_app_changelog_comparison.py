"""Changelog comparison — side-by-side comparison of two versions."""


def compare_changelogs(*, version_a: dict, version_b: dict) -> dict:
    a_changes = set(c.get("description", "") for c in version_a.get("changes", []))
    b_changes = set(c.get("description", "") for c in version_b.get("changes", []))
    return {
        "version_a": version_a.get("version"), "version_b": version_b.get("version"),
        "only_in_a": sorted(a_changes - b_changes), "only_in_b": sorted(b_changes - a_changes),
        "common": sorted(a_changes & b_changes), "total_unique": len(a_changes | b_changes),
    }

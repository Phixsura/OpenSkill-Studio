"""App comparison — compare two apps side by side."""


def compare_apps(app_a: dict, app_b: dict) -> dict:
    """Compare two apps for marketplace comparison view."""
    fields = ["category", "status", "visibility"]
    differences = {}
    for f in fields:
        va, vb = app_a.get(f), app_b.get(f)
        if va != vb:
            differences[f] = {"a": va, "b": vb}

    perms_a = set(app_a.get("permissions", []))
    perms_b = set(app_b.get("permissions", []))
    
    return {
        "app_a": {"name": app_a.get("name"), "id": app_a.get("id")},
        "app_b": {"name": app_b.get("name"), "id": app_b.get("id")},
        "differences": differences,
        "permissions": {
            "only_a": sorted(perms_a - perms_b),
            "only_b": sorted(perms_b - perms_a),
            "shared": sorted(perms_a & perms_b),
        },
        "install_comparison": {
            "a": app_a.get("install_count", 0),
            "b": app_b.get("install_count", 0),
        },
    }

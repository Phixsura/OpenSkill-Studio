"""Permissions page builder — build permissions overview for app detail."""

def build_permissions_page(*, permissions: list[str], manifest_permissions: list[str]) -> dict:
    read = [p for p in permissions if p.startswith("read:")]
    write = [p for p in permissions if p.startswith("write:")]
    special = [p for p in permissions if not p.startswith(("read:", "write:"))]
    return {"permissions": permissions, "total": len(permissions),
            "read": read, "write": write, "special": special,
            "read_count": len(read), "write_count": len(write), "special_count": len(special)}

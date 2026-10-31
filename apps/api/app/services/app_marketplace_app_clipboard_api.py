"""Clipboard API — generate copyable code snippets and share links."""

import html
import secrets


def generate_install_snippet(*, app_id: str, package_name: str,
                                manager: str = "npm") -> dict:
    managers = {
        "npm": f"npm install {package_name}",
        "yarn": f"yarn add {package_name}",
        "pnpm": f"pnpm add {package_name}",
        "pip": f"pip install {package_name}",
        "uv": f"uv add {package_name}",
    }
    if manager not in managers:
        return {"error": f"Unknown manager. Valid: {', '.join(sorted(managers))}"}
    return {
        "command": managers[manager],
        "manager": manager,
        "package": package_name,
        "all_commands": managers,
    }


def generate_share_link(*, resource_type: str, resource_id: str,
                           base_url: str = "https://marketplace.openskill.dev") -> dict:
    paths = {
        "app": f"/apps/{resource_id}",
        "collection": f"/collections/{resource_id}",
        "developer": f"/developers/{resource_id}",
        "review": f"/reviews/{resource_id}",
    }
    path = paths.get(resource_type)
    if not path:
        return {"error": f"Unknown resource type. Valid: {', '.join(sorted(paths))}"}
    url = f"{base_url}{path}"
    return {"url": url, "short_url": f"https://osk.link/{secrets.token_urlsafe(6)}",
            "embed_code": f'<a href="{html.escape(url)}">{html.escape(resource_type)}</a>'}

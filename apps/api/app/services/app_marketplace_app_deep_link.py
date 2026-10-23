"""App deep link — generate and resolve deep links for apps."""

import urllib.parse
import secrets


def generate_deep_link(*, app_id: str, action: str = "open",
                        params: dict | None = None) -> dict:
    base = f"openskill://marketplace/app/{app_id}"
    query = {"action": action}
    if params:
        query.update(params)
    url = f"{base}?{urllib.parse.urlencode(query)}"
    short_code = secrets.token_urlsafe(6)
    return {
        "deep_link": url,
        "short_link": f"https://osk.link/{short_code}",
        "web_fallback": f"https://marketplace.openskill.dev/apps/{app_id}",
        "qr_url": f"https://api.openskill.dev/qr?data={urllib.parse.quote(url)}",
    }


def resolve_deep_link(*, url: str) -> dict:
    if not url.startswith("openskill://"):
        return {"resolved": False, "error": "Not an OpenSkill deep link"}
    parts = urllib.parse.urlparse(url)
    path_parts = [p for p in parts.path.strip("/").split("/") if p]
    query = dict(urllib.parse.parse_qsl(parts.query))
    return {
        "resolved": True,
        "scheme": parts.scheme,
        "host": parts.netloc,
        "path_segments": path_parts,
        "params": query,
        "action": query.get("action", "open"),
    }

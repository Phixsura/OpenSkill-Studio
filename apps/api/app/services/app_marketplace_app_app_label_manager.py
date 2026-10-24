"""Label manager — tag and label CRUD with color assignment."""

import html
import re
import hashlib

LABEL_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9 _-]{0,49}$")
COLORS = ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"]


def auto_color(name: str) -> str:
    idx = int(hashlib.md5(name.encode()).hexdigest()[:4], 16) % len(COLORS)
    return COLORS[idx]


def create_label(*, name: str, color: str | None = None, description: str = "") -> dict:
    if not LABEL_RE.match(name):
        return {"error": "Invalid label name (alphanumeric, spaces, hyphens, underscores, max 50)"}
    c = color or auto_color(name)
    return {"name": name, "color": c, "description": html.escape(description), "slug": name.lower().replace(" ", "-")}


def build_label_list(*, labels: list[dict]) -> dict:
    items = [{"name": html.escape(l.get("name", "")), "color": l.get("color", auto_color(l.get("name", ""))),
              "count": l.get("count", 0)} for l in labels]
    items.sort(key=lambda x: -x["count"])
    return {"labels": items, "total": len(items)}

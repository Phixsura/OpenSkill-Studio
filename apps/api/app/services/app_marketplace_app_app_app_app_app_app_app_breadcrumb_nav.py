"""Breadcrumb navigator — build navigation breadcrumbs from URL paths."""
from __future__ import annotations
import html


ROUTE_LABELS = {
    "": "Home", "apps": "Apps", "settings": "Settings", "analytics": "Analytics",
    "billing": "Billing", "team": "Team", "webhooks": "Webhooks",
    "docs": "Documentation", "api": "API", "security": "Security",
    "deployments": "Deployments", "monitoring": "Monitoring",
}


def build_breadcrumbs(path: str) -> list[dict]:
    segments = [s for s in path.strip("/").split("/") if s]
    crumbs = [{"label": "Home", "path": "/", "active": False}]
    current_path = ""
    for i, seg in enumerate(segments):
        current_path += f"/{seg}"
        label = ROUTE_LABELS.get(seg, html.escape(seg.replace("-", " ").replace("_", " ").title()))
        crumbs.append({
            "label": label, "path": current_path,
            "active": i == len(segments) - 1,
        })
    return crumbs


def get_parent_path(path: str) -> str:
    parts = path.rstrip("/").rsplit("/", 1)
    return parts[0] if len(parts) > 1 and parts[0] else "/"

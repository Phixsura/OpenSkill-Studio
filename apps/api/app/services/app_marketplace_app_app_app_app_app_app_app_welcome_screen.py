"""Welcome screen — personalized welcome for first-time and returning users."""
from __future__ import annotations
import html


def build_welcome(*, user_name: str, is_new: bool, stats: dict | None = None) -> dict:
    name = html.escape(user_name)
    if is_new:
        return {
            "type": "new_user", "greeting": f"Welcome, {name}! 👋",
            "message": "Let's get you started on the OpenSkill platform.",
            "steps": ["Create your first app", "Generate an API key", "Make your first API call"],
            "cta": {"label": "Get Started", "path": "/getting-started"},
        }
    return {
        "type": "returning", "greeting": f"Welcome back, {name}! 👋",
        "message": "Here's what's happened since your last visit.",
        "stats": stats or {},
        "cta": {"label": "Go to Dashboard", "path": "/dashboard"},
    }

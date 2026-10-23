"""App marketplace success page — post-action success confirmations."""
from __future__ import annotations
import html


def build_success_page(*, action: str, app_name: str = "",
                         details: dict | None = None) -> dict:
    messages = {
        "installed": {"title": "App Installed! 🎉", "body": f"{html.escape(app_name)} has been installed successfully.",
                       "next": ["Configure webhooks", "Set up API keys", "View documentation"]},
        "published": {"title": "App Published! 🚀", "body": f"{html.escape(app_name)} is now live on the marketplace.",
                        "next": ["Monitor analytics", "Respond to reviews", "Share with developers"]},
        "deployed": {"title": "Deploy Complete! ✅", "body": f"Version deployed successfully.",
                       "next": ["Check health status", "Monitor error rate", "Review logs"]},
        "upgraded": {"title": "Plan Upgraded! ⬆️", "body": "Your plan has been upgraded.",
                       "next": ["Explore new features", "Update API limits", "Invite team members"]},
    }
    msg = messages.get(action, {"title": "Success! ✅", "body": "Action completed.", "next": []})
    return {**msg, "action": action, "app_name": html.escape(app_name),
            "details": details or {}, "show_confetti": action in ("installed", "published")}

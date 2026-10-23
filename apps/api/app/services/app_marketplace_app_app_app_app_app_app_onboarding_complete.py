"""Onboarding complete — the final onboarding completion celebration page."""

import html
from datetime import datetime, timezone

NEXT_STEPS = [
    {"label": "Create Your First App", "href": "/apps/new", "icon": "📦", "primary": True},
    {"label": "Browse Marketplace", "href": "/marketplace", "icon": "🏪"},
    {"label": "Read the Docs", "href": "/docs", "icon": "📖"},
    {"label": "Join Community", "href": "/community", "icon": "💬"},
    {"label": "Set Up Webhooks", "href": "/webhooks", "icon": "🔗"},
    {"label": "Connect Integrations", "href": "/integrations", "icon": "🔌"},
]


def build_onboarding_complete(*, user_name: str, plan: str = "free") -> dict:
    return {
        "headline": f"🎉 Welcome aboard, {html.escape(user_name)}!",
        "subtitle": "Your account is ready. Here's what you can do next.",
        "plan": plan, "plan_label": plan.title(),
        "next_steps": NEXT_STEPS,
        "step_count": len(NEXT_STEPS),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

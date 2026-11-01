"""Integration wizard — guided setup for third-party integrations."""
from __future__ import annotations
import html

INTEGRATIONS = {
    "slack": {"name": "Slack", "icon": "💬", "steps": ["Authorize", "Select Channel", "Configure Events", "Test"]},
    "github": {"name": "GitHub", "icon": "🐙", "steps": ["Authorize", "Select Repos", "Configure Webhooks", "Test"]},
    "stripe": {"name": "Stripe", "icon": "💳", "steps": ["Connect Account", "Configure Products", "Test Payment"]},
    "jira": {"name": "Jira", "icon": "📋", "steps": ["Authorize", "Map Projects", "Sync Issues", "Test"]},
}


def get_integration(integration_id: str) -> dict | None:
    i = INTEGRATIONS.get(integration_id)
    return {"id": integration_id, **i, "step_count": len(i["steps"])} if i else None


def build_wizard(integration_id: str, *, current_step: int = 0) -> dict:
    integ = INTEGRATIONS.get(integration_id)
    if not integ:
        return {"error": "Integration not found"}
    steps = [{"index": i, "title": s, "status": "completed" if i < current_step else
              "current" if i == current_step else "pending"}
             for i, s in enumerate(integ["steps"])]
    pct = round(current_step / len(integ["steps"]) * 100)
    return {"integration": integration_id, "name": integ["name"], "icon": integ["icon"],
            "steps": steps, "current_step": current_step, "total_steps": len(steps),
            "progress_pct": pct, "complete": current_step >= len(steps)}


def list_integrations() -> list[dict]:
    return [{"id": k, "name": v["name"], "icon": v["icon"], "steps": len(v["steps"])}
            for k, v in INTEGRATIONS.items()]

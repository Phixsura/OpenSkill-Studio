"""Getting started guide — personalized onboarding guide for new developers."""
from __future__ import annotations

GUIDES = {
    "build_app": {"title": "Build Your First App", "icon": "📱", "steps": [
        "Create a new app in the Developer Console",
        "Configure app settings and permissions",
        "Implement your app logic",
        "Submit for marketplace review"]},
    "integrate_api": {"title": "Integrate the API", "icon": "🔌", "steps": [
        "Generate an API key",
        "Install the SDK for your language",
        "Make your first API call",
        "Handle webhooks"]},
    "deploy": {"title": "Deploy to Production", "icon": "🚀", "steps": [
        "Set up CI/CD pipeline",
        "Configure environment variables",
        "Run tests and security scan",
        "Deploy and monitor"]},
}


def get_guide(guide_id: str) -> dict:
    guide = GUIDES.get(guide_id)
    if not guide:
        return {"error": f"Guide not found: {guide_id}"}
    return {"id": guide_id, **guide, "step_count": len(guide["steps"])}


def list_guides() -> list[dict]:
    return [{"id": k, "title": v["title"], "icon": v["icon"],
             "step_count": len(v["steps"])} for k, v in GUIDES.items()]


def recommend_guide(*, has_app: bool, has_api_key: bool, has_deploy: bool) -> str:
    if not has_app:
        return "build_app"
    if not has_api_key:
        return "integrate_api"
    if not has_deploy:
        return "deploy"
    return "build_app"

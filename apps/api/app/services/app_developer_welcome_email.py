"""Developer welcome email."""

def build_welcome_email(developer_name: str, slug: str) -> dict:
    return {"subject": f"Welcome to OpenSkill Developer Platform, {developer_name}!",
            "greeting": f"Hi {developer_name},", "cta": {"label": "Get Started", "url": f"/dashboard/developer"}}

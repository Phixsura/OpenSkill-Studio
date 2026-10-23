"""Onboarding email — welcome email sequence for new developers."""

import html


def generate_welcome_email(*, developer_name: str, plan: str) -> dict:
    safe_name = html.escape(developer_name)
    subject = f"Welcome to OpenSkill, {safe_name}! 🎉"
    steps = [
        {"step": 1, "title": "Complete your profile", "url": "/settings/profile"},
        {"step": 2, "title": "Create your first app", "url": "/apps/new"},
        {"step": 3, "title": "Explore the SDK docs", "url": "/docs/sdk"},
        {"step": 4, "title": "Join the community", "url": "/community"},
    ]
    return {
        "subject": subject,
        "developer_name": safe_name,
        "plan": plan,
        "steps": steps,
        "cta_label": "Get Started",
        "cta_url": "https://marketplace.openskill.dev/getting-started",
    }


def generate_day_3_email(*, developer_name: str, apps_created: int) -> dict:
    safe_name = html.escape(developer_name)
    if apps_created == 0:
        message = "You haven't created an app yet. Let's get started!"
        cta = "Create Your First App"
    elif apps_created == 1:
        message = "Great job creating your first app! Here's how to get more installs."
        cta = "Optimize Your Listing"
    else:
        message = f"You've created {apps_created} apps! Check out advanced features."
        cta = "Explore Advanced Features"
    return {"subject": f"Day 3 Tips for {safe_name}", "message": message, "cta": cta}

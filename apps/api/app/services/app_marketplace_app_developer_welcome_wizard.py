"""Developer welcome wizard — personalized onboarding based on developer experience."""

def build_welcome_flow(*, experience: str, goals: list[str]) -> dict:
    valid_exp = {"beginner", "intermediate", "expert"}
    if experience not in valid_exp:
        experience = "beginner"
    steps = {
        "beginner": [
            {"title": "Welcome to OpenSkill!", "content": "Let's build your first app together."},
            {"title": "Create Developer Account", "action": "create_account"},
            {"title": "Explore Templates", "action": "browse_templates"},
            {"title": "Build Your First App", "action": "create_app"},
            {"title": "Submit for Review", "action": "submit_review"},
        ],
        "intermediate": [
            {"title": "Welcome Back!", "content": "Ready to level up?"},
            {"title": "Import Existing Project", "action": "import_project"},
            {"title": "Configure Webhooks", "action": "setup_webhooks"},
            {"title": "Set Up CI/CD", "action": "setup_pipeline"},
        ],
        "expert": [
            {"title": "Welcome, Expert!", "content": "Jump right in."},
            {"title": "API & SDK Setup", "action": "sdk_setup"},
            {"title": "Advanced Configuration", "action": "advanced_config"},
        ],
    }
    return {"experience": experience, "goals": goals, "steps": steps.get(experience, []),
            "step_count": len(steps.get(experience, [])), "estimated_minutes": len(steps.get(experience, [])) * 3}

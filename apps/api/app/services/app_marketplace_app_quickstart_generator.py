"""Quickstart generator — auto-generate getting-started guides for apps."""


def generate_quickstart(*, app: dict, installation_steps: list[str] | None = None,
                          config_fields: list[dict] | None = None) -> dict:
    steps = installation_steps or [
        f"Navigate to the OpenSkill Marketplace and find **{app['name']}**",
        "Click **Install** and select your organization",
        "Review and grant the requested permissions",
        "Configure the app settings for your team",
    ]
    config_section = []
    for field in (config_fields or []):
        config_section.append(f"- **{field['name']}**: {field.get('description', 'No description')} "
                              f"(default: `{field.get('default', 'none')}`)")
    return {
        "app_name": app["name"],
        "sections": [
            {"title": "Installation", "content": "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))},
            {"title": "Configuration", "content": "\n".join(config_section) or "No configuration required."},
            {"title": "Usage", "content": f"Once installed, {app['name']} will automatically handle events based on your configuration."},
            {"title": "Support", "content": f"For help, visit the {app['name']} documentation or contact the developer."},
        ],
        "estimated_setup_minutes": 5,
    }


def render_quickstart_markdown(*, quickstart: dict) -> str:
    lines = [f"# Getting Started with {quickstart['app_name']}\n"]
    for section in quickstart["sections"]:
        lines.append(f"## {section['title']}\n")
        lines.append(section["content"])
        lines.append("")
    lines.append(f"---\n*Estimated setup time: {quickstart['estimated_setup_minutes']} minutes*")
    return "\n".join(lines)

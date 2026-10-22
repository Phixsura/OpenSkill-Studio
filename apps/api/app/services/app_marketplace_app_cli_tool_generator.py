"""CLI tool generator — generate CLI commands for common app operations."""


def generate_install_command(*, app_slug: str, org_id: str) -> str:
    return f"openskill apps install {app_slug} --org {org_id}"


def generate_config_command(*, app_slug: str, key: str, value: str) -> str:
    return f"openskill apps config set {app_slug} {key}={value}"


def generate_cli_reference(*, app: dict, commands: list[str] | None = None) -> dict:
    default_commands = [
        {"command": f"openskill apps info {app['slug']}", "description": "View app details"},
        {"command": f"openskill apps install {app['slug']}", "description": "Install the app"},
        {"command": f"openskill apps update {app['slug']}", "description": "Update to latest version"},
        {"command": f"openskill apps uninstall {app['slug']}", "description": "Uninstall the app"},
        {"command": f"openskill apps logs {app['slug']}", "description": "View app logs"},
        {"command": f"openskill apps config {app['slug']}", "description": "Manage configuration"},
    ]
    return {"app_name": app["name"], "commands": default_commands}

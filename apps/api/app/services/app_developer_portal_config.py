"""Developer portal config — configuration for the developer portal UI."""

PORTAL_CONFIG = {
    "features": {
        "app_creation": True,
        "webhook_testing": True,
        "sandbox_execution": True,
        "api_key_management": True,
        "analytics_dashboard": True,
        "marketplace_listing": True,
        "team_management": True,
        "billing": False,  # Coming soon
    },
    "limits": {
        "max_apps_free": 3,
        "max_apps_standard": 10,
        "max_apps_premium": 50,
    },
    "links": {
        "docs": "/docs/developer",
        "api_reference": "/docs/api",
        "sdk_typescript": "https://www.npmjs.com/package/@openskill/sdk",
        "sdk_python": "https://pypi.org/project/openskill-sdk/",
        "community": "https://github.com/Phixsura/OpenSkill-Studio/discussions",
    },
}


def get_portal_config() -> dict:
    return PORTAL_CONFIG


def is_feature_enabled(feature: str) -> bool:
    return PORTAL_CONFIG["features"].get(feature, False)

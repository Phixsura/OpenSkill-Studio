"""Global config — platform-wide configuration values."""

PLATFORM_CONFIG = {
    "platform_name": "OpenSkill Marketplace",
    "platform_url": "https://openskill.dev",
    "api_base_url": "https://api.openskill.dev",
    "cdn_url": "https://cdn.openskill.dev",
    "docs_url": "https://docs.openskill.dev",
    "support_email": "support@openskill.dev",
    "max_apps_per_developer": {"free": 1, "starter": 5, "pro": 25, "enterprise": -1},
    "max_file_upload_mb": 50,
    "supported_languages": ["en", "zh", "ja", "ko", "es", "fr", "de", "pt"],
    "review_sla_days": 3,
    "platform_version": "2.1.0",
}


def get_config(*, key: str, default: object = None) -> object:
    return PLATFORM_CONFIG.get(key, default)


def get_all_config() -> dict:
    return dict(PLATFORM_CONFIG)


def get_public_config() -> dict:
    public_keys = {"platform_name", "platform_url", "docs_url", "supported_languages",
                    "review_sla_days", "platform_version"}
    return {k: v for k, v in PLATFORM_CONFIG.items() if k in public_keys}

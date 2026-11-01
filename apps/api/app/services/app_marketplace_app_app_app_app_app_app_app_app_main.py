"""Main app — the OpenSkill platform main application entry point."""

from datetime import datetime, timezone


def build_main_app_config() -> dict:
    return {
        "app": {"name": "OpenSkill Developer Platform", "version": "16.0.0",
                "environment": "production"},
        "features": {
            "marketplace": True, "developer_console": True, "webhooks": True,
            "analytics": True, "api_keys": True, "team_management": True,
            "billing": True, "sso": True, "2fa": True, "audit_logs": True,
        },
        "routes": [
            {"path": "/", "page": "landing"},
            {"path": "/marketplace", "page": "marketplace_home"},
            {"path": "/console", "page": "developer_console"},
            {"path": "/docs", "page": "documentation"},
            {"path": "/pricing", "page": "pricing"},
            {"path": "/status", "page": "platform_status"},
            {"path": "/community", "page": "community"},
        ],
        "api": {"base_url": "https://api.openskill.dev", "version": "v1",
                "rate_limit": {"rpm": 1000, "burst": 100}},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

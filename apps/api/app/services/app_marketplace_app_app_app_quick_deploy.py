"""App quick deploy — one-click deployment flow."""

import secrets
import html
from datetime import datetime, timezone


def start_quick_deploy(*, app_id: str, version: str, environment: str = "production") -> dict:
    deploy_id = f"dep_{secrets.token_hex(8)}"
    return {
        "deploy_id": deploy_id, "app_id": app_id, "version": version,
        "environment": environment, "status": "deploying",
        "steps": [
            {"name": "Build", "status": "running", "icon": "🔨"},
            {"name": "Test", "status": "pending", "icon": "🧪"},
            {"name": "Deploy", "status": "pending", "icon": "🚀"},
            {"name": "Verify", "status": "pending", "icon": "✅"},
        ],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "estimated_seconds": 120,
    }


def complete_deploy(*, deploy_id: str, success: bool) -> dict:
    return {
        "deploy_id": deploy_id,
        "status": "success" if success else "failed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "message": "🎉 Deployed successfully!" if success else "❌ Deployment failed",
    }

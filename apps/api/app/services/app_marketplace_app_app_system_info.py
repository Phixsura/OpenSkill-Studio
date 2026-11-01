"""System info — runtime environment and version information."""

import platform
import sys


def get_system_info() -> dict:
    return {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "hostname": platform.node()[:20],  # truncate for privacy
        "api_version": "2.0.0",
        "runtime": f"Python {sys.version_info.major}.{sys.version_info.minor}",
    }


def build_about_page(*, app_name: str = "OpenSkill Marketplace",
                       version: str = "2.0.0") -> dict:
    sys_info = get_system_info()
    return {
        "app_name": app_name,
        "version": version,
        "runtime": sys_info["runtime"],
        "platform": sys_info["platform"],
        "components": [
            {"name": "API Server", "version": version, "status": "operational"},
            {"name": "Web Frontend", "version": version, "status": "operational"},
            {"name": "Database", "version": "PostgreSQL 16", "status": "operational"},
            {"name": "Cache", "version": "Redis 7", "status": "operational"},
        ],
        "links": {
            "docs": "/docs",
            "api_reference": "/api/v1/docs",
            "changelog": "/changelog",
            "status": "/status",
        },
    }

"""Data export page — GDPR-compliant data export with format options."""


def build_data_export_page(*, user: dict, available_exports: list[dict],
                               recent_exports: list[dict]) -> dict:
    return {
        "page_type": "data_export",
        "user": {"name": user.get("display_name"), "email": user.get("email")},
        "available_exports": [
            {"id": "profile", "label": "Profile Data", "description": "Your account information", "icon": "👤",
             "formats": ["json", "csv"], "estimated_size_kb": 50},
            {"id": "apps", "label": "App Data", "description": "All your apps and configurations", "icon": "📦",
             "formats": ["json"], "estimated_size_kb": 500},
            {"id": "analytics", "label": "Analytics Data", "description": "Usage metrics and statistics", "icon": "📊",
             "formats": ["json", "csv"], "estimated_size_kb": 2000},
            {"id": "reviews", "label": "Reviews", "description": "Reviews you've written", "icon": "⭐",
             "formats": ["json", "csv"], "estimated_size_kb": 100},
            {"id": "full", "label": "Complete Export", "description": "Everything in one package", "icon": "📁",
             "formats": ["json", "zip"], "estimated_size_kb": 5000},
        ],
        "recent_exports": recent_exports[:5],
        "gdpr_info": {"retention_days": 30, "processing_time": "Up to 48 hours",
                        "deletion_url": "/settings/privacy/delete"},
    }


def request_export(*, user_id: str, export_type: str, format: str) -> dict:
    valid_types = {"profile", "apps", "analytics", "reviews", "full"}
    if export_type not in valid_types:
        return {"success": False, "error": f"Invalid export type: {export_type}"}
    return {"success": True, "export_type": export_type, "format": format,
            "status": "processing", "estimated_minutes": 30 if export_type == "full" else 5,
            "message": f"Your {export_type} export is being prepared. We'll email you when it's ready."}

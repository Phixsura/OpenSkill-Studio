"""App uninstall — app removal with data cleanup options."""

import html
import secrets
from datetime import datetime, timezone

DATA_TYPES = ["configuration", "webhooks", "api_keys", "cached_data", "user_preferences"]


def build_uninstall_flow(*, app_name: str, app_id: str,
                           data_sizes: dict[str, int] | None = None) -> dict:
    items = []
    total_size = 0
    for dt in DATA_TYPES:
        size = (data_sizes or {}).get(dt, 0)
        total_size += size
        items.append({"type": dt, "label": dt.replace("_", " ").title(),
                       "size_kb": size, "will_delete": True})
    return {
        "app_name": html.escape(app_name), "app_id": app_id,
        "data_to_remove": items, "total_size_kb": total_size,
        "total_size_display": f"{total_size}KB" if total_size < 1024 else f"{total_size/1024:.1f}MB",
        "warning": f"All data for {html.escape(app_name)} will be permanently deleted.",
    }


def confirm_uninstall(*, app_id: str) -> dict:
    return {"app_id": app_id, "status": "uninstalled",
            "uninstalled_at": datetime.now(timezone.utc).isoformat(),
            "message": "App has been uninstalled successfully."}

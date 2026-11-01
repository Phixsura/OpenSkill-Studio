"""App data export — format app data for export."""

import json

def export_app_data(app: dict, *, versions: list[dict] | None = None, include_secrets: bool = False) -> str:
    data = {"export_version": "1.0", "app": {k: v for k, v in app.items() if k != "oauth_client_secret_hash"},
            "versions": versions or []}
    if not include_secrets:
        for v in data.get("versions", []):
            v.pop("signing_key", None)
    return json.dumps(data, indent=2, default=str)

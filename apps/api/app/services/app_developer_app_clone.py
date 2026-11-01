"""App clone — create a copy of an existing app for development."""

import copy
import secrets


def clone_app(app: dict, *, new_name: str, new_slug: str) -> dict:
    """Clone an app's configuration for a new app."""
    cloned = copy.deepcopy(app)
    # Reset identity
    cloned["id"] = f"app_{secrets.token_hex(12)}"
    cloned["name"] = new_name
    cloned["slug"] = new_slug
    cloned["status"] = "draft"
    cloned["visibility"] = "private"
    cloned["install_count"] = 0
    # Clear OAuth credentials
    cloned.pop("oauth_client_id", None)
    cloned.pop("oauth_client_secret_hash", None)
    cloned.pop("created_at", None)
    cloned.pop("updated_at", None)
    return cloned

"""API keys page builder — compile API key management page data."""

def build_api_keys_page(*, keys: list[dict], max_keys: int = 5) -> dict:
    active = [k for k in keys if not k.get("revoked")]
    return {"keys": keys, "active_count": len(active), "total": len(keys),
            "max": max_keys, "can_create": len(active) < max_keys}

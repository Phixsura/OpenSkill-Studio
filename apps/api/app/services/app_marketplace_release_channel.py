"""Release channel — manage stable, beta, and canary release channels."""


CHANNELS = {
    "stable": {"label": "Stable", "icon": "✅", "auto_update": True, "risk": "low"},
    "beta": {"label": "Beta", "icon": "🧪", "auto_update": False, "risk": "medium"},
    "canary": {"label": "Canary", "icon": "🐤", "auto_update": False, "risk": "high"},
    "internal": {"label": "Internal", "icon": "🔒", "auto_update": False, "risk": "high"},
}


def get_channels(*, app_id: str, versions: dict[str, str]) -> dict:
    result = []
    for ch_id, meta in CHANNELS.items():
        ver = versions.get(ch_id)
        result.append({
            "id": ch_id, **meta, "current_version": ver,
            "has_release": ver is not None,
        })
    return {"app_id": app_id, "channels": result,
            "active_channels": sum(1 for r in result if r["has_release"])}


def promote_release(*, from_channel: str, to_channel: str, version: str) -> dict:
    order = ["canary", "beta", "stable"]
    if from_channel not in order or to_channel not in order:
        return {"error": "Invalid channel"}
    if order.index(from_channel) >= order.index(to_channel):
        return {"error": f"Cannot promote from {from_channel} to {to_channel}"}
    return {"promoted": True, "version": version,
            "from": from_channel, "to": to_channel,
            "message": f"v{version} promoted from {from_channel} to {to_channel}"}

"""Release channels — stable, beta, canary distribution tracks."""

from datetime import datetime, timezone

VALID_CHANNELS = {"stable", "beta", "canary", "rc"}


def assign_channel(*, version_id: str, channel: str, promoted_by: str) -> dict:
    if channel not in VALID_CHANNELS:
        return {"error": f"Invalid channel. Use: {', '.join(sorted(VALID_CHANNELS))}"}
    return {
        "version_id": version_id, "channel": channel, "promoted_by": promoted_by,
        "promoted_at": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def get_latest_by_channel(*, versions: list[dict], channel: str) -> dict | None:
    matching = [v for v in versions if v.get("channel") == channel]
    if not matching:
        return None
    return max(matching, key=lambda v: v.get("released_at", ""))


def promote_to_stable(*, version: dict) -> dict:
    if version.get("channel") not in ("beta", "rc"):
        return {"error": "Only beta or rc versions can be promoted to stable"}
    return {**version, "channel": "stable", "promoted_at": datetime.now(timezone.utc).isoformat(), "error": None}


def list_channels_summary(*, versions: list[dict]) -> list[dict]:
    channels = {}
    for v in versions:
        ch = v.get("channel", "stable")
        if ch not in channels or v.get("released_at", "") > channels[ch].get("released_at", ""):
            channels[ch] = v
    return [{"channel": ch, "version": v.get("version"), "released_at": v.get("released_at")} for ch, v in sorted(channels.items())]

"""Version badge — display app version with release channel info."""


def build_version_badge(*, version: str, channel: str = "stable",
                           is_latest: bool = True) -> dict:
    channels = {
        "stable": {"color": "green", "icon": "✅", "label": "Stable"},
        "beta": {"color": "yellow", "icon": "🧪", "label": "Beta"},
        "canary": {"color": "orange", "icon": "🐤", "label": "Canary"},
        "rc": {"color": "blue", "icon": "🔵", "label": "Release Candidate"},
    }
    ch = channels.get(channel, channels["stable"])
    return {
        "version": version,
        "channel": channel,
        "channel_info": ch,
        "is_latest": is_latest,
        "display": f"v{version}" if not version.startswith("v") else version,
        "full_label": f"v{version} ({ch['label']})",
    }

"""App Release Channel — manage stable/beta/canary release tracks for developer apps.

Supports progressive rollout via release channels:
- Channel types: stable, beta, canary, internal
- Per-installation channel subscription
- Version pinning per channel
- Channel promotion: canary → beta → stable
- Rollback to previous channel version
- Channel-aware version resolution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class Channel(str, Enum):
    STABLE = "stable"
    BETA = "beta"
    CANARY = "canary"
    INTERNAL = "internal"


CHANNEL_ORDER = {Channel.INTERNAL: 0, Channel.CANARY: 1, Channel.BETA: 2, Channel.STABLE: 3}


@dataclass
class ChannelRelease:
    """A version published to a channel."""

    app_id: str
    channel: Channel
    version: str
    published_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    previous_version: str | None = None
    notes: str = ""


@dataclass
class ChannelSubscription:
    """An installation's channel subscription."""

    installation_id: str
    app_id: str
    channel: Channel
    pinned_version: str | None = None   # None = follow latest


@dataclass
class ResolvedVersion:
    """The version an installation should run."""

    version: str
    channel: Channel
    is_pinned: bool
    source: str  # "pinned", "channel_latest", "fallback_stable"


class AppReleaseChannel:
    """Manage release channels and version resolution."""

    def __init__(self):
        # (app_id, channel) → list of ChannelRelease (newest first)
        self._releases: dict[tuple[str, Channel], list[ChannelRelease]] = {}
        # installation_id → ChannelSubscription
        self._subscriptions: dict[str, ChannelSubscription] = {}

    # ── Publishing ───────────────────────────────────────

    def publish(self, app_id: str, channel: Channel, version: str,
                notes: str = "") -> ChannelRelease:
        """Publish a version to a channel."""
        key = (app_id, channel)
        releases = self._releases.get(key, [])
        previous = releases[0].version if releases else None

        release = ChannelRelease(
            app_id=app_id, channel=channel, version=version,
            previous_version=previous, notes=notes,
        )
        self._releases.setdefault(key, []).insert(0, release)
        log.info("release.published", app_id=app_id, channel=channel.value, version=version)
        return release

    def promote(self, app_id: str, from_channel: Channel,
                to_channel: Channel) -> ChannelRelease | None:
        """Promote the latest version from one channel to another.

        Only promotes upward: canary → beta → stable.
        """
        if CHANNEL_ORDER[to_channel] <= CHANNEL_ORDER[from_channel]:
            return None  # can't promote downward

        source = self.get_latest(app_id, from_channel)
        if source is None:
            return None

        return self.publish(app_id, to_channel, source.version,
                            notes=f"Promoted from {from_channel.value}")

    def rollback(self, app_id: str, channel: Channel) -> ChannelRelease | None:
        """Rollback to the previous version on a channel."""
        key = (app_id, channel)
        releases = self._releases.get(key, [])
        if len(releases) < 2:
            return None

        previous = releases[1]
        return self.publish(app_id, channel, previous.version,
                            notes=f"Rollback from {releases[0].version}")

    # ── Querying ─────────────────────────────────────────

    def get_latest(self, app_id: str, channel: Channel) -> ChannelRelease | None:
        releases = self._releases.get((app_id, channel), [])
        return releases[0] if releases else None

    def get_history(self, app_id: str, channel: Channel,
                    limit: int = 10) -> list[ChannelRelease]:
        return self._releases.get((app_id, channel), [])[:limit]

    def list_channels(self, app_id: str) -> dict[str, str | None]:
        """List all channels with their latest version for an app."""
        result: dict[str, str | None] = {}
        for ch in Channel:
            latest = self.get_latest(app_id, ch)
            result[ch.value] = latest.version if latest else None
        return result

    # ── Subscriptions ────────────────────────────────────

    def subscribe(self, installation_id: str, app_id: str,
                  channel: Channel) -> ChannelSubscription:
        sub = ChannelSubscription(
            installation_id=installation_id, app_id=app_id, channel=channel,
        )
        self._subscriptions[installation_id] = sub
        return sub

    def pin_version(self, installation_id: str, version: str) -> bool:
        sub = self._subscriptions.get(installation_id)
        if sub is None:
            return False
        sub.pinned_version = version
        return True

    def unpin_version(self, installation_id: str) -> bool:
        sub = self._subscriptions.get(installation_id)
        if sub is None:
            return False
        sub.pinned_version = None
        return True

    def get_subscription(self, installation_id: str) -> ChannelSubscription | None:
        return self._subscriptions.get(installation_id)

    # ── Version resolution ───────────────────────────────

    def resolve_version(self, installation_id: str) -> ResolvedVersion | None:
        """Resolve which version an installation should run.

        Priority: pinned > channel latest > fallback to stable.
        """
        sub = self._subscriptions.get(installation_id)
        if sub is None:
            return None

        # Pinned version
        if sub.pinned_version:
            return ResolvedVersion(
                version=sub.pinned_version, channel=sub.channel,
                is_pinned=True, source="pinned",
            )

        # Channel latest
        latest = self.get_latest(sub.app_id, sub.channel)
        if latest:
            return ResolvedVersion(
                version=latest.version, channel=sub.channel,
                is_pinned=False, source="channel_latest",
            )

        # Fallback to stable
        if sub.channel != Channel.STABLE:
            stable = self.get_latest(sub.app_id, Channel.STABLE)
            if stable:
                return ResolvedVersion(
                    version=stable.version, channel=Channel.STABLE,
                    is_pinned=False, source="fallback_stable",
                )

        return None

"""Tests for App Release Channel — publish, promote, rollback, subscriptions, resolution."""

import pytest

from app.services.app_release_channel import (
    AppReleaseChannel,
    Channel,
)


class TestPublish:
    def test_publish_to_channel(self):
        rc = AppReleaseChannel()
        rel = rc.publish("app-1", Channel.CANARY, "1.0.0-alpha.1")
        assert rel.version == "1.0.0-alpha.1"
        assert rel.channel == Channel.CANARY
        assert rel.previous_version is None

    def test_publish_tracks_previous(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rel = rc.publish("app-1", Channel.STABLE, "1.1.0")
        assert rel.previous_version == "1.0.0"

    def test_latest_is_newest(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.publish("app-1", Channel.STABLE, "2.0.0")
        latest = rc.get_latest("app-1", Channel.STABLE)
        assert latest.version == "2.0.0"

    def test_channels_independent(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.publish("app-1", Channel.BETA, "2.0.0-beta.1")
        assert rc.get_latest("app-1", Channel.STABLE).version == "1.0.0"
        assert rc.get_latest("app-1", Channel.BETA).version == "2.0.0-beta.1"


class TestPromote:
    def test_promote_canary_to_beta(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.CANARY, "2.0.0-alpha.1")
        promoted = rc.promote("app-1", Channel.CANARY, Channel.BETA)
        assert promoted is not None
        assert promoted.version == "2.0.0-alpha.1"
        assert promoted.channel == Channel.BETA

    def test_promote_beta_to_stable(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.BETA, "2.0.0-beta.1")
        promoted = rc.promote("app-1", Channel.BETA, Channel.STABLE)
        assert promoted.channel == Channel.STABLE

    def test_promote_downward_blocked(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        assert rc.promote("app-1", Channel.STABLE, Channel.BETA) is None

    def test_promote_same_channel_blocked(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.BETA, "1.0.0")
        assert rc.promote("app-1", Channel.BETA, Channel.BETA) is None

    def test_promote_empty_source(self):
        rc = AppReleaseChannel()
        assert rc.promote("app-1", Channel.CANARY, Channel.STABLE) is None


class TestRollback:
    def test_rollback_to_previous(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.publish("app-1", Channel.STABLE, "1.1.0")
        rolled = rc.rollback("app-1", Channel.STABLE)
        assert rolled is not None
        assert rolled.version == "1.0.0"
        assert rc.get_latest("app-1", Channel.STABLE).version == "1.0.0"

    def test_rollback_no_previous(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        assert rc.rollback("app-1", Channel.STABLE) is None

    def test_rollback_empty_channel(self):
        rc = AppReleaseChannel()
        assert rc.rollback("app-1", Channel.STABLE) is None


class TestHistory:
    def test_history_ordered(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.publish("app-1", Channel.STABLE, "1.1.0")
        rc.publish("app-1", Channel.STABLE, "1.2.0")
        history = rc.get_history("app-1", Channel.STABLE)
        versions = [r.version for r in history]
        assert versions[0] == "1.2.0"  # newest first

    def test_history_limit(self):
        rc = AppReleaseChannel()
        for i in range(10):
            rc.publish("app-1", Channel.STABLE, f"1.{i}.0")
        assert len(rc.get_history("app-1", Channel.STABLE, limit=3)) == 3

    def test_list_channels(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.publish("app-1", Channel.BETA, "2.0.0-beta")
        channels = rc.list_channels("app-1")
        assert channels["stable"] == "1.0.0"
        assert channels["beta"] == "2.0.0-beta"
        assert channels["canary"] is None


class TestSubscriptions:
    def test_subscribe(self):
        rc = AppReleaseChannel()
        sub = rc.subscribe("inst-1", "app-1", Channel.BETA)
        assert sub.channel == Channel.BETA
        assert sub.pinned_version is None

    def test_pin_version(self):
        rc = AppReleaseChannel()
        rc.subscribe("inst-1", "app-1", Channel.STABLE)
        assert rc.pin_version("inst-1", "1.0.0") is True
        sub = rc.get_subscription("inst-1")
        assert sub.pinned_version == "1.0.0"

    def test_unpin_version(self):
        rc = AppReleaseChannel()
        rc.subscribe("inst-1", "app-1", Channel.STABLE)
        rc.pin_version("inst-1", "1.0.0")
        rc.unpin_version("inst-1")
        assert rc.get_subscription("inst-1").pinned_version is None

    def test_pin_nonexistent(self):
        rc = AppReleaseChannel()
        assert rc.pin_version("nonexistent", "1.0.0") is False


class TestVersionResolution:
    def test_resolve_channel_latest(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.subscribe("inst-1", "app-1", Channel.STABLE)
        resolved = rc.resolve_version("inst-1")
        assert resolved.version == "1.0.0"
        assert resolved.source == "channel_latest"
        assert resolved.is_pinned is False

    def test_resolve_pinned(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "2.0.0")
        rc.subscribe("inst-1", "app-1", Channel.STABLE)
        rc.pin_version("inst-1", "1.0.0")
        resolved = rc.resolve_version("inst-1")
        assert resolved.version == "1.0.0"
        assert resolved.source == "pinned"
        assert resolved.is_pinned is True

    def test_resolve_fallback_to_stable(self):
        rc = AppReleaseChannel()
        rc.publish("app-1", Channel.STABLE, "1.0.0")
        rc.subscribe("inst-1", "app-1", Channel.BETA)
        # No beta release → fallback to stable
        resolved = rc.resolve_version("inst-1")
        assert resolved.version == "1.0.0"
        assert resolved.channel == Channel.STABLE
        assert resolved.source == "fallback_stable"

    def test_resolve_no_subscription(self):
        rc = AppReleaseChannel()
        assert rc.resolve_version("nonexistent") is None

    def test_resolve_no_releases(self):
        rc = AppReleaseChannel()
        rc.subscribe("inst-1", "app-1", Channel.STABLE)
        assert rc.resolve_version("inst-1") is None

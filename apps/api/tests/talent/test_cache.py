"""Tests for talent layer Redis cache module."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest


# ── Module-level import tests ──


def test_cache_module_importable():
    from app.talent.services import cache

    assert hasattr(cache, "get_cached")
    assert hasattr(cache, "set_cached")
    assert hasattr(cache, "invalidate")
    assert hasattr(cache, "profile_cache_key")
    assert hasattr(cache, "match_cache_key")
    assert hasattr(cache, "user_match_cache_key")


def test_profile_cache_key_format():
    from app.talent.services.cache import profile_cache_key

    assert profile_cache_key("USER123") == "talent:profile:USER123"


def test_match_cache_key_format():
    from app.talent.services.cache import match_cache_key

    assert match_cache_key("OPP456", 50) == "talent:match:OPP456:50"
    assert match_cache_key("OPP456") == "talent:match:OPP456:20"


def test_user_match_cache_key_format():
    from app.talent.services.cache import user_match_cache_key

    assert user_match_cache_key("USR789") == "talent:match_user:USR789:20"


# ── Cache operation tests ──


@pytest.mark.asyncio
async def test_get_cached_returns_parsed_json():
    from app.talent.services.cache import get_cached

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=json.dumps({"score": 0.85}))

    with patch("app.talent.services.cache._redis", return_value=mock_redis):
        result = await get_cached("talent:profile:U1")
        assert result == {"score": 0.85}


@pytest.mark.asyncio
async def test_get_cached_returns_none_on_miss():
    from app.talent.services.cache import get_cached

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)

    with patch("app.talent.services.cache._redis", return_value=mock_redis):
        result = await get_cached("talent:profile:NONEXISTENT")
        assert result is None


@pytest.mark.asyncio
async def test_get_cached_returns_none_on_error():
    from app.talent.services.cache import get_cached

    with patch("app.talent.services.cache._redis", side_effect=ConnectionError("down")):
        result = await get_cached("talent:profile:U1")
        assert result is None


@pytest.mark.asyncio
async def test_set_cached_writes_with_ttl():
    from app.talent.services.cache import set_cached

    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock()

    with patch("app.talent.services.cache._redis", return_value=mock_redis):
        await set_cached("talent:profile:U1", {"score": 0.9}, ttl=120)
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == "talent:profile:U1"
        assert json.loads(call_args[0][1]) == {"score": 0.9}
        assert call_args[1]["ex"] == 120


@pytest.mark.asyncio
async def test_set_cached_graceful_on_error():
    from app.talent.services.cache import set_cached

    with patch("app.talent.services.cache._redis", side_effect=ConnectionError("down")):
        await set_cached("key", {"data": 1})  # Should not raise


@pytest.mark.asyncio
async def test_invalidate_graceful_on_no_redis():
    from app.talent.services.cache import invalidate

    with patch("app.talent.services.cache._redis", side_effect=ConnectionError("down")):
        await invalidate("talent:profile:*")  # Should not raise


@pytest.mark.asyncio
async def test_invalidate_deletes_matching_keys():
    from app.talent.services.cache import invalidate

    mock_redis = AsyncMock()
    mock_redis.scan = AsyncMock(
        side_effect=[(0, ["talent:profile:U1", "talent:profile:U2"])]
    )
    mock_redis.delete = AsyncMock()

    with patch("app.talent.services.cache._redis", return_value=mock_redis):
        await invalidate("talent:profile:*")
        mock_redis.delete.assert_called_once_with(
            "talent:profile:U1", "talent:profile:U2"
        )


# ── Scoring integration tests ──


def test_scoring_cache_key_matches_expected_format():
    from app.talent.services.cache import profile_cache_key

    key = profile_cache_key("01ABCDEFGHIJKLMNOP0123456")
    assert key.startswith("talent:profile:")
    assert "01ABCDEFGHIJKLMNOP0123456" in key


def test_capability_score_dataclass_is_serializable():
    from app.talent.services.scoring import CapabilityScore

    now = datetime.now(timezone.utc)
    score = CapabilityScore(
        capability_id="CAP1",
        capability_name="Python",
        level=3,
        level_label="Advanced",
        score=0.85,
        depth=0.9,
        breadth=0.7,
        recency=0.8,
        velocity=0.6,
        confidence=0.95,
        evidence_count=5,
        substantial_evidence_count=3,
        last_verified_at=now,
        verification_mix={"peer": 3, "self": 2},
        scoring_version="2.0.0",
        computed_at=now,
    )
    d = asdict(score)
    assert d["capability_id"] == "CAP1"
    assert d["score"] == 0.85
    serialized = json.dumps(d, default=str)
    deserialized = json.loads(serialized)
    assert deserialized["capability_name"] == "Python"
    assert deserialized["level"] == 3


def test_migration_file_exists():
    import os

    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "migrations",
        "versions",
        "talent15_performance_indexes.py",
    )
    assert os.path.exists(path)


def test_migration_has_correct_revision():
    import importlib.util
    import os

    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "migrations",
        "versions",
        "talent15_performance_indexes.py",
    )
    spec = importlib.util.spec_from_file_location("talent15", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.revision == "talent15a00015"
    assert mod.down_revision == "talent14a00014"

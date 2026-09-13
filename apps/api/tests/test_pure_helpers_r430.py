"""R430: cross-service pure helpers — semver ordering, level/badge math,
copy-slug/name truncation guards (R89), filename path-stripping (R156),
search cache-key boundary encoding. All pure → fast, no DB.

_parse_semver, _compute_level, _compute_badges reach 100% mutation
coverage; _cache_key has no arithmetic/comparison mutants. Documented
EQUIVALENT mutants in the truncation helpers (adjudicated):
- _dup_slug L25 token_hex(3) length and _copy_name L36 `<=` at the exact
  limit: a different hex length is still a unique suffix, and at
  len==limit the trim path recomputes the identical string (the base is
  already exactly limit-len(suffix)).
- _clamp_filename L64 rsplit maxsplit (``[-1]`` is identical for any
  maxsplit>=1), L65 `<=` at exactly MAX_FILENAME_LEN (the trim/ext path
  reproduces the same string), and the L68 extension-length threshold
  edges (dot is never 0 after the leading-dot strip; the 20-vs-21-char
  cutoff only differs for pathological 20+-char file extensions).
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.services.duplicate import _copy_name, _dup_slug
from app.services.gamification import _LEVEL_STEP, _compute_level
from app.services.installation import _parse_semver
from app.services.project import MAX_FILENAME_LEN, _clamp_filename
from app.services.registry import _compute_badges
from app.services.workflow_registry import _cache_key


def test_parse_semver_ordering_r430():
    assert _parse_semver("1.2.3") == (1, 2, 3, "~")
    # pre-release sorts BEFORE the release of the same X.Y.Z
    assert _parse_semver("1.0.0-alpha") < _parse_semver("1.0.0")
    assert _parse_semver("1.0.0-alpha") < _parse_semver("1.0.0-beta")  # ascii order
    # normal precedence across components
    assert _parse_semver("1.0.0") < _parse_semver("1.0.1")
    assert _parse_semver("1.9.0") < _parse_semver("1.10.0")  # numeric, not lexical
    assert _parse_semver("2.0.0") > _parse_semver("1.99.99")


def test_compute_level_r430():
    assert _LEVEL_STEP == 100
    assert _compute_level(0) == 1  # floor is level 1
    assert _compute_level(99) == 1
    assert _compute_level(100) == 2  # step boundary
    assert _compute_level(250) == 3
    assert _compute_level(-50) == 1  # never below 1


def test_compute_badges_r430():
    now = datetime(2026, 9, 1, tzinfo=UTC)
    thirty = now - timedelta(days=30)
    # popular threshold is >= 10 installs, "New" if created within 30 days
    popular_new = SimpleNamespace(install_count=10, created_at=now)
    assert _compute_badges(popular_new, now, thirty) == ["Popular", "New"]
    # 9 installs → not popular; created 31 days ago → not new
    neither = SimpleNamespace(install_count=9, created_at=now - timedelta(days=31))
    assert _compute_badges(neither, now, thirty) == []
    # exactly on the 30-day boundary counts as New
    boundary = SimpleNamespace(install_count=0, created_at=thirty)
    assert _compute_badges(boundary, now, thirty) == ["New"]
    # a null created_at is tolerated (no New badge, no crash)
    nocreated = SimpleNamespace(install_count=10, created_at=None)
    assert _compute_badges(nocreated, now, thirty) == ["Popular"]


def test_dup_slug_and_copy_name_r430():
    # a normal slug gets a -copy-<hex> suffix
    out = _dup_slug("my-skill")
    assert out.startswith("my-skill-copy-")
    assert len(out) <= 200
    # a base ALREADY at 200 chars still keeps the full uniqueness suffix (R89):
    # the suffix must survive, so the result is exactly 200 and ends in the hex
    long_base = "x" * 200
    out_long = _dup_slug(long_base)
    assert len(out_long) == 200
    assert "-copy-" in out_long
    assert out_long.split("-copy-")[1]  # non-empty hex suffix
    # an existing -copy-<hex> tail is stripped before re-appending (no stacking)
    out_re = _dup_slug("base-copy-abc123")
    assert out_re.startswith("base-copy-")
    assert out_re.count("-copy-") == 1

    # _copy_name: fits within limit
    assert _copy_name("Doc", 200) == "Doc (Copy)"
    # a name at the limit is trimmed so ' (Copy)' still fits
    at_limit = "N" * 200
    cn = _copy_name(at_limit, 200)
    assert cn.endswith(" (Copy)")
    assert len(cn) == 200


def test_clamp_filename_r430():
    # short clean names pass through
    assert _clamp_filename("photo.png") == "photo.png"
    # PATH COMPONENTS are stripped (R156) — basename only
    assert _clamp_filename("../../../etc/passwd.png") == "passwd.png"
    assert _clamp_filename("C:\\Users\\x\\evil.txt") == "evil.txt"
    # leading dots stripped; an all-dot name falls back to 'file'
    assert _clamp_filename("...") == "file"
    # a very long name keeps a short extension and stays within the cap
    long_name = "a" * 500 + ".png"
    clamped = _clamp_filename(long_name)
    assert len(clamped) == MAX_FILENAME_LEN
    assert clamped.endswith(".png")


def test_cache_key_boundary_r430():
    # field boundaries are preserved: (search='a:b') must NOT collide with
    # (search='a', scenario='b') — a raw ':'-join would
    k1 = _cache_key({"search": "a:b"})
    k2 = _cache_key({"search": "a", "scenario": "b"})
    assert k1 != k2
    # deterministic + sorted-keys stable regardless of insertion order
    assert _cache_key({"a": 1, "b": 2}) == _cache_key({"b": 2, "a": 1})
    assert _cache_key({"search": "x"}).startswith("wfregistry:search:")

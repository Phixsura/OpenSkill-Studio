"""Tests for the workflow registry cache layer (ADR-010, R15 batch B).

The search cache stores only {ids, total}; these tests pin down the cache
key construction (no cross-field collisions) and the warm-read semantics
for empty pages (total must survive the round trip).
"""

import pytest

from app.services.workflow_registry import WorkflowRegistryService, _cache_key

# ── Cache key construction ────────────────────────────────


def test_cache_key_no_collision_on_colon_values():
    """The old ':'-joined key collided when values themselves contain ':' —
    search='Bypass:x' + scenario='y' vs search='Bypass' + scenario='x:y'
    both produced 'Bypass:x:y:...'. The JSON-based key must keep field
    boundaries distinct."""
    k1 = _cache_key({"search": "Bypass:x", "scenario": "y"})
    k2 = _cache_key({"search": "Bypass", "scenario": "x:y"})
    assert k1 != k2


def test_cache_key_distinguishes_none_from_literal_none_string():
    k1 = _cache_key({"search": None, "scenario": "a"})
    k2 = _cache_key({"search": "None", "scenario": "a"})
    assert k1 != k2


def test_cache_key_keeps_invalidation_prefix():
    """Invalidation deletes 'wfregistry:*' — the key must stay under it."""
    assert _cache_key({"search": "x"}).startswith("wfregistry:")


def test_cache_key_deterministic():
    params = {"search": "hero", "page": 2, "per_page": 20}
    assert _cache_key(params) == _cache_key(dict(params))


# ── Warm-read semantics ───────────────────────────────────


@pytest.mark.asyncio
async def test_cached_empty_page_preserves_total(monkeypatch):
    """A warm empty page (e.g. page beyond the last result) must return the
    cached catalog total, not 0 — clients read meta.total from the current
    page to render page counts."""
    from app.services import workflow_registry as wr

    async def fake_cache_get(key):
        return {"ids": [], "total": 7}

    monkeypatch.setattr(wr, "cache_get", fake_cache_get)
    # The empty-ids cache-hit path returns before touching the DB
    svc = WorkflowRegistryService(db=None)
    packs, total = await svc.search_packs(search="anything", page=99)
    assert packs == []
    assert total == 7

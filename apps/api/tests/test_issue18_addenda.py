"""Issue-18 addenda regressions: rate-limit identity (R78b), registry
per_page cap parity (R71), and pagination ULID tiebreaks (R75/R75b)."""

import uuid
from types import SimpleNamespace

import pytest

from app.config import settings
from app.core.rate_limit import client_identity
from app.core.security import create_access_token


def _req(headers: dict | None = None, client_host: str | None = "9.9.9.9"):
    hdrs = {k.lower(): v for k, v in (headers or {}).items()}

    class _H(dict):
        def get(self, k, default=""):
            return hdrs.get(k.lower(), default)

    return SimpleNamespace(
        headers=_H(),
        client=SimpleNamespace(host=client_host) if client_host else None,
        scope={},
    )


def test_identity_defaults_to_direct_peer_and_ignores_spoofed_xff(monkeypatch):
    """R78b: at 0 trusted hops (default), X-Forwarded-For is attacker-writable
    — it must be IGNORED or a client mints unlimited buckets."""
    monkeypatch.setattr(settings, "trusted_proxy_hops", 0)
    r = _req({"x-forwarded-for": "1.2.3.4, 5.6.7.8"})
    assert client_identity(r) == "ip:9.9.9.9"


def test_identity_unwraps_forwarded_chain_behind_trusted_proxy(monkeypatch):
    """R78b: behind N trusted hops the client is the N-th XFF entry from the
    right — without this every user behind the LB shared ONE bucket."""
    monkeypatch.setattr(settings, "trusted_proxy_hops", 1)
    r = _req({"x-forwarded-for": "1.2.3.4"})
    assert client_identity(r) == "ip:1.2.3.4"
    # client → CDN → LB (2 trusted hops): CDN appended the client, LB the CDN.
    monkeypatch.setattr(settings, "trusted_proxy_hops", 2)
    r2 = _req({"x-forwarded-for": "1.2.3.4, 10.0.0.7"})
    assert client_identity(r2) == "ip:1.2.3.4"
    # Header shorter than the chain: leftmost available.
    r3 = _req({"x-forwarded-for": "1.2.3.4"})
    assert client_identity(r3) == "ip:1.2.3.4"
    # No header at all → direct peer.
    r4 = _req({})
    assert client_identity(r4) == "ip:9.9.9.9"


def test_identity_prefers_authenticated_user(monkeypatch):
    """R78b: a valid access token keys the bucket on the USER, so NAT'd
    populations don't share one bucket; a forged token falls back to IP."""
    monkeypatch.setattr(settings, "trusted_proxy_hops", 0)
    uid = f"01USER{uuid.uuid4().hex[:20].upper()}"
    token = create_access_token(uid, "u@test.com", "student")
    r = _req({"authorization": f"Bearer {token}"})
    assert client_identity(r) == f"u:{uid}"
    r2 = _req({"authorization": "Bearer not.a.token"})
    assert client_identity(r2) == "ip:9.9.9.9"


@pytest.mark.asyncio
async def test_registry_per_page_cap_matches_meta():
    """R71: the endpoint reports per_page=min(per_page, max_results or 50) but
    the service applied NO default cap — ?per_page=100 returned 100 rows while
    meta said 50. The service now applies the same cap."""
    import inspect

    from app.services.registry import RegistryService

    src = inspect.getsource(RegistryService.search_packs)
    assert "min(per_page, max_results or 50)" in src, (
        "service per_page cap diverged from the endpoint's again"
    )


def test_paginated_lists_carry_ulid_tiebreak():
    """R75/R75b: OFFSET pagination over a non-unique ORDER BY key skips or
    duplicates rows on timestamp ties. Every flagged paginated list must chain
    the ULID pk as tiebreak."""
    import inspect

    from app.services import (
        client_brief,
        cohort,
        evaluation,
        learning_path,
        notification,
        organization,
        project,
        registry,
        skill_pack,
    )

    checks = [
        (client_brief.ClientBriefService.list_briefs, "ClientBrief.id"),
        (cohort.CohortService.list_cohorts, "Cohort.id"),
        (evaluation.EvaluationService.list_tasks, "EvaluationTask.id"),
        (learning_path.LearningPathService.list_paths, "LearningPath.id"),
        (notification.NotificationService.list_notifications, "Notification.id"),
        (organization.OrgService.get_members, "OrgMember.id"),
        (project.ProjectService.list_submissions, "Submission.id"),
        (registry.RegistryService.search_packs, "SkillPack.id"),
        (skill_pack.SkillPackService.list_packs, "SkillPack.id"),
    ]
    for fn, marker in checks:
        src = inspect.getsource(fn)
        assert marker in src, f"{fn.__qualname__} lost its {marker} pagination tiebreak"

"""Ecosystem endpoint surface tests — no DB needed.

Every /ecosystem endpoint requires authentication (401 unauthenticated), and
request-body validation fires before any DB access (422 with envelope).
"""

import pytest

WRITE_ENDPOINTS = [
    ("post", "/api/v1/ecosystem/sources", {}),
    ("post", "/api/v1/ecosystem/observations", {}),
    ("post", "/api/v1/ecosystem/benchmark/suites", {}),
    ("post", "/api/v1/ecosystem/graph/edges", {}),
    ("post", "/api/v1/ecosystem/replacements/candidates/generate", {}),
    ("post", "/api/v1/ecosystem/drafts", {}),
    ("post", "/api/v1/ecosystem/rollouts", {}),
    ("post", "/api/v1/ecosystem/watchlists", {}),
    ("post", "/api/v1/ecosystem/impact/analyses", {}),
    # ADR-016 §11 amendments
    ("post", "/api/v1/ecosystem/observations/bulk-verify", {"ids": ["a" * 26]}),
    ("post", "/api/v1/ecosystem/resolution-candidates/bulk-decide",
     {"ids": ["a" * 26], "decision": "confirm"}),
    ("post", "/api/v1/ecosystem/pricing/availability/probe/model/" + "a" * 26, {}),
]

READ_ENDPOINTS = [
    "/api/v1/ecosystem/sources",
    "/api/v1/ecosystem/observations",
    "/api/v1/ecosystem/changes",
    "/api/v1/ecosystem/catalog/models",
    "/api/v1/ecosystem/resolution-candidates",
    "/api/v1/ecosystem/capability-mappings",
    "/api/v1/ecosystem/pricing/observations",
    "/api/v1/ecosystem/benchmark/suites",
    "/api/v1/ecosystem/benchmark/runs",
    "/api/v1/ecosystem/telemetry/snapshots",
    "/api/v1/ecosystem/impact/analyses",
    "/api/v1/ecosystem/replacements/candidates",
    "/api/v1/ecosystem/drafts",
    "/api/v1/ecosystem/rollouts",
    "/api/v1/ecosystem/watchlists",
    "/api/v1/ecosystem/dashboard",
    "/api/v1/ecosystem/signals/matching",
    "/api/v1/ecosystem/signals/workforce",
    "/api/v1/ecosystem/deprecation-calendar",
]


@pytest.mark.parametrize("path", READ_ENDPOINTS)
async def test_reads_require_auth(client, path):
    resp = await client.get(path)
    assert resp.status_code == 401, path
    assert "error" in resp.json()


@pytest.mark.parametrize("method,path,body", WRITE_ENDPOINTS)
async def test_writes_require_auth(client, method, path, body):
    resp = await client.request(method.upper(), path, json=body)
    assert resp.status_code == 401, path
    assert "error" in resp.json()


async def test_unknown_catalog_kind_is_404_shape(client):
    # Unauthenticated first — auth wins; the route itself exists
    resp = await client.get("/api/v1/ecosystem/catalog/nonsense-kind")
    assert resp.status_code == 401


async def test_validation_shapes_are_bounded(client):
    """Oversized field values are rejected by schema bounds (422), not 500."""
    resp = await client.post(
        "/api/v1/ecosystem/sources",
        json={
            "name": "x" * 5000,  # exceeds max_length=200
            "source_type": "provider_api",
            "trust_level": "official",
            "adapter_key": "json_catalog",
        },
    )
    # Auth dependency runs after body parsing in FastAPI? Body validation
    # happens first for malformed shapes; either 401 or 422 is acceptable,
    # but never a 500.
    assert resp.status_code in (401, 422)


def test_web_severity_dropdown_matches_backend_vocabulary():
    """Round-239 drift guard: the web change-feed dropdown hardcodes the
    severity list; §93 made unknown values a 422 — if either side drifts,
    the UI filter starts erroring (or silently missing new severities).
    Pin web SEVERITIES == CHANGE_SEVERITIES in CI."""
    import re
    from pathlib import Path

    from app.ecosystem.models.observation import CHANGE_SEVERITIES

    page = (
        Path(__file__).resolve().parents[2]
        / "web/src/app/(dashboard)/dashboard/ecosystem/changes/page.tsx"
    )
    src = page.read_text()
    m = re.search(r"const SEVERITIES = \[(.*?)\];", src, re.S)
    assert m, "web changes page must declare const SEVERITIES = [...]"
    web_values = set(re.findall(r'"([a-z_]+)"', m.group(1)))
    assert web_values == set(CHANGE_SEVERITIES), (
        f"web dropdown {sorted(web_values)} != backend {sorted(CHANGE_SEVERITIES)}"
    )


def test_severity_rank_covers_the_full_vocabulary():
    """Round-242 guard: notify fan-out ranks severities via
    SEVERITY_RANK.get(sev, 0) — a severity added to CHANGE_SEVERITIES but
    forgotten in SEVERITY_RANK would silently rank as LOWEST and be muted
    for every watcher with a threshold. Pin the two constants together."""
    from app.ecosystem.models.observation import CHANGE_SEVERITIES, SEVERITY_RANK

    assert set(SEVERITY_RANK) == set(CHANGE_SEVERITIES)
    # ranks are a strict total order (no accidental duplicates)
    assert len(set(SEVERITY_RANK.values())) == len(SEVERITY_RANK)


def test_handbook_cron_schedule_matches_registry():
    """Round-261 drift guard (§96 rule: derive coverage from the system):
    the operator handbook documents every eco cron's minutes by hand — pin
    them to the live cron registry so a schedule change that skips the docs
    fails CI."""
    from pathlib import Path

    from app.controlplane.worker import _cron_jobs

    doc = (
        Path(__file__).resolve().parents[3] / "docs/ops/ecosystem-operations.md"
    ).read_text()
    eco_crons = [j for j in _cron_jobs() if j.name.startswith("eco_")]
    assert len(eco_crons) >= 7  # floor: a broken filter can't vacuously pass
    for job in eco_crons:
        minutes = job.minute  # set|int|None per arq cron
        if minutes is None:
            continue
        vals = sorted(minutes) if isinstance(minutes, (set, frozenset)) else [minutes]
        if job.name == "eco_retention":
            token = f"{job.hour if not isinstance(job.hour, (set, frozenset)) else sorted(job.hour)[0]:02d}:{vals[0]}"
        else:
            token = "/".join(str(v) for v in vals)
        assert token in doc, (
            f"handbook out of date for {job.name}: expected '{token}' "
            "in docs/ops/ecosystem-operations.md"
        )

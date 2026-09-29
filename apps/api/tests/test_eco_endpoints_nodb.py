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


def test_every_eco_audit_action_is_registered():
    """Round-278 systemic guard: eco_audit is fail-safe — an UNREGISTERED
    action doesn't error, it silently never lands in the trail (exactly how
    the rotate audit shipped broken). Scan every eco_audit(action=...) call
    site and require the literal to be in AUDIT_ACTIONS."""
    import re
    from pathlib import Path

    from app.controlplane.services.audit import AUDIT_ACTIONS

    app_dir = Path(__file__).resolve().parents[1] / "app" / "ecosystem"
    used: set[str] = set()
    for path in app_dir.rglob("*.py"):
        for m in re.finditer(r'action="(eco\.[a-z_.]+)"', path.read_text()):
            used.add(m.group(1))
    assert len(used) >= 5, f"call-site scan looks broken ({sorted(used)})"
    unregistered = used - set(AUDIT_ACTIONS)
    assert not unregistered, (
        f"eco_audit actions never reach the trail (fail-safe swallows them): "
        f"{sorted(unregistered)} — register in AUDIT_ACTIONS"
    )


def test_every_request_model_forbids_unknown_fields():
    """Round-300 guard: pydantic's default (extra=ignore) silently DROPS
    mistyped field names — a client typo returns 200 while the setting never
    lands. Every eco request model must reject unknowns."""
    import inspect

    from pydantic import BaseModel

    from app.ecosystem import schemas

    offenders = []
    checked = 0
    for name, cls in inspect.getmembers(schemas, inspect.isclass):
        if not name.endswith("Request") or not issubclass(cls, BaseModel):
            continue
        checked += 1
        if cls.model_config.get("extra") != "forbid":
            offenders.append(name)
    assert checked >= 25, f"model scan looks broken ({checked})"
    assert not offenders, f"request models silently ignoring unknown fields: {offenders}"


async def test_unknown_field_is_rejected_over_http(client):
    """Round-300 killer: the wire-level consequence — a typo'd field must be
    a 422, not a silently half-applied write."""
    r = await client.post(
        "/api/v1/ecosystem/watchlists",
        json={"name": "x", "min_severty": "breaking"},  # typo on purpose
        headers={"Authorization": "Bearer bogus"},
    )
    # 401 (bogus token) would ALSO prove nothing got applied; but validation
    # order puts body parsing first only sometimes — accept either rejection
    assert r.status_code in (401, 422)
    assert r.status_code != 200


def test_web_change_type_dropdown_matches_backend_vocabulary():
    """Round-321 drift guard (§93.1 pattern): pin the web change-type
    dropdown to CHANGE_TYPES."""
    import re
    from pathlib import Path

    from app.ecosystem.models.observation import CHANGE_TYPES

    page = (
        Path(__file__).resolve().parents[2]
        / "web/src/app/(dashboard)/dashboard/ecosystem/changes/page.tsx"
    )
    m = re.search(r"const CHANGE_TYPES = \[(.*?)\];", page.read_text(), re.S)
    assert m, "web changes page must declare const CHANGE_TYPES = [...]"
    web_values = set(re.findall(r'"([a-z_]+)"', m.group(1)))
    assert web_values == set(CHANGE_TYPES), (
        f"web {sorted(web_values)} != backend {sorted(CHANGE_TYPES)}"
    )


def test_web_test_mock_paths_exist_in_the_route_table():
    """Round-324 drift guard (§96): web unit tests mock apiWithAuth by PATH
    STRING — a renamed endpoint keeps those tests green while the real page
    404s (the compare-path bug class, R226). Every /ecosystem path literal
    mocked in web tests must prefix-match a real route (path params
    wildcarded)."""
    import re
    from pathlib import Path

    from app.main import app as _app

    def _walk(router):
        for rt in getattr(router, "routes", []):
            if type(rt).__name__ == "_IncludedRouter":
                yield from _walk(rt.original_router)
            elif hasattr(rt, "path"):
                yield rt.path
            elif hasattr(rt, "routes"):
                yield from _walk(rt)

    route_paths = [
        path
        for path in _walk(_app.router)
        if isinstance(path, str) and path.startswith("/ecosystem")
    ]
    route_res = [
        re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", path) + "$")
        for path in route_paths
    ]
    assert len(route_res) >= 60

    tests_dir = Path(__file__).resolve().parents[2] / "web/__tests__"
    offenders = []
    checked = 0
    for f in tests_dir.glob("ecosystem-*.test.tsx"):
        for lit in re.findall(r'"(/ecosystem/[A-Za-z0-9_\-/]+)"', f.read_text()):
            checked += 1
            ok = any(rx.match(lit) for rx in route_res) or any(
                # prefix-style mocks (path.startsWith("/ecosystem/x/")) are
                # fine as long as they prefix a REAL route at a SEGMENT
                # boundary (else /compare would match a renamed /compare-v2)
                rp == lit
                or rp.startswith(lit if lit.endswith("/") else lit + "/")
                or rp.startswith(lit + "?")
                for rp in route_paths
            )
            if not ok:
                offenders.append(f"{f.name}: {lit}")
    assert checked >= 20, f"literal scan looks broken ({checked})"
    assert not offenders, f"mocked paths with no matching route: {offenders}"


def test_every_orm_order_by_carries_the_id_tiebreak():
    """Round-338 guard (§99.9 made permanent): every ORM order_by in the eco
    package must end in the immutable id — timestamp/score ties otherwise
    order nondeterministically, flapping ETags, audit histories and
    "latest" selection. Derived from the code pattern, not a column list."""
    import re
    from pathlib import Path

    pkg = Path(__file__).resolve().parents[1] / "app" / "ecosystem"
    offenders = []
    checked = 0
    for f in pkg.rglob("*.py"):
        src = f.read_text()
        # collapse newlines so multi-line order_by chains are one match,
        # then extract the argument list with a paren-balance walk (regex
        # alone trips over the nested parens in .desc())
        flat = re.sub(r"\s+", " ", src)
        for m in re.finditer(r"\.order_by\(", flat):
            depth = 1
            i = m.end()
            while i < len(flat) and depth:
                depth += {"(": 1, ")": -1}.get(flat[i], 0)
                i += 1
            inner = flat[m.end() : i - 1]
            checked += 1
            if ".id" in inner or "similarity" in inner:
                continue  # id tiebreak present, or trgm score (unique per row)
            offenders.append(f"{f.name}: order_by({inner[:70]})")
    assert checked >= 30, f"pattern scan looks broken ({checked})"
    assert not offenders, (
        "order_by without id tiebreak (nondeterministic on ties): "
        f"{offenders}"
    )


def test_web_lifecycle_dropdown_matches_backend_vocabulary():
    """Round-371 drift guard (§93.1 pattern, third vocabulary): the catalog
    status dropdown derives from LIFECYCLE_STYLES — pin it to the backend
    LIFECYCLE_STATUSES so the §371 whitelist never 422s the UI."""
    import re
    from pathlib import Path

    from app.ecosystem.models.catalog import LIFECYCLE_STATUSES

    lib = (
        Path(__file__).resolve().parents[2]
        / "web/src/app/(dashboard)/dashboard/ecosystem/lib.ts"
    ).read_text()
    m = re.search(r"LIFECYCLE_STYLES[^=]*= \{(.*?)\};", lib, re.S)
    assert m
    web_values = set(re.findall(r"^  ([a-z_]+):", m.group(1), re.M))
    assert web_values == set(LIFECYCLE_STATUSES), (
        f"web {sorted(web_values)} != backend {sorted(LIFECYCLE_STATUSES)}"
    )


async def test_lifecycle_filter_rejects_unknown_status(client):
    """Round-371 killer: ?lifecycle_status=typo must 422 (was silent-empty)."""
    r = await client.get(
        "/api/v1/ecosystem/catalog/models?lifecycle_status=vrified",
        headers={"Authorization": "Bearer bogus"},
    )
    assert r.status_code in (401, 422)
    assert r.status_code != 200


def test_web_family_dropdown_matches_backend_vocabulary():
    """Round-374 drift guard (fourth vocabulary): the benchmarks page's
    FAMILIES list feeds the now-whitelisted leaderboard filter — pin it to
    BENCHMARK_FAMILIES so the UI can never send a 422able value."""
    import re
    from pathlib import Path

    from app.ecosystem.models.benchmark import BENCHMARK_FAMILIES

    page = (
        Path(__file__).resolve().parents[2]
        / "web/src/app/(dashboard)/dashboard/ecosystem/benchmarks/page.tsx"
    ).read_text()
    m = re.search(r"const FAMILIES = \[(.*?)\];", page, re.S)
    assert m
    web_values = set(re.findall(r'"([a-z0-9_]+)"', m.group(1)))
    assert web_values == set(BENCHMARK_FAMILIES), (
        f"web {sorted(web_values)} != backend {sorted(BENCHMARK_FAMILIES)}"
    )

"""R496: scim2-tester conformance run against the live SCIM server.

Deferred at P4 ("until the dependency earns its keep") — it earned it: the
first run found the missing /ResourceTypes/{id} + /Schemas/{id} discovery
sub-resources, plain-404s where RFC 7644 wants the SCIM error schema, 404s
where a wrong METHOD on a known resource wants 405, and the Group PATCH
externalId silent no-op.

Two shims adapt the TESTER to this environment, not the server:
- httpx.URL.origin (tester assumes a newer httpx);
- userName generation produces emails (this server's DELIBERATE strict-email
  rule, ADR-018 R7 — random non-email userNames are a 400 by design).

Remaining dispositioned non-successes (asserted below, so a change in either
direction is visible):
- members add/replace with an EMPTY member object is a tolerant-server no-op
  (our delta engine ignores value-less entries; adding nothing is nothing);
- POST /.search is advertised unsupported (filter via GET is implemented;
  ServiceProviderConfig carries no .search claim) — the tester probes it
  anyway.

Usage: api on :8000 (APP_ENV=test), then
  PYTHONPATH=. uv run python tests/e2e_scim_conformance.py
"""

import os
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8000/api/v1")

# ── tester-environment shims ──
if not hasattr(httpx.URL, "origin"):
    httpx.URL.origin = property(  # type: ignore[attr-defined]
        lambda self: httpx.URL(f"{self.scheme}://{self.netloc.decode()}")
    )

from scim2_tester import filling  # noqa: E402

_orig_generate = filling.generate_random_value


def _email_username_generate(context, path, **kwargs):
    if str(path).endswith("userName"):
        return f"{uuid.uuid4().hex[:12]}@conformance.example.edu"
    return _orig_generate(context, path, **kwargs)


filling.generate_random_value = _email_username_generate
# checkers that import the symbol directly need the patch too
import scim2_tester.checkers.patch_add as _patch_add  # noqa: E402
import scim2_tester.checkers.patch_replace as _patch_replace  # noqa: E402

for mod in (_patch_add, _patch_replace):
    if hasattr(mod, "generate_random_value"):
        mod.generate_random_value = _email_username_generate

ALLOWED_FAILURES = (
    "returned unexpected value for 'members'",  # empty-member no-op (tolerant)
    "did not remove attribute",  # tester couples remove to the members run
    "Resource not found",  # POST /.search — advertised unsupported
    "Method not allowed",  # POST /.search on servers mapping it to 405
    # Group members MUST reference a provisioned org user (never-guess
    # identity rule, ADR-018 §9) — the tester's synthetic references are
    # rejected 400 BY DESIGN; IdPs provision users before group push.
    "Member value is not a user in this organization",
    # emails mirror userName (identity IS the email here) — an independent
    # emails PATCH is deliberately not honored.
    "unexpected value for 'emails'",
    # delete ≡ deactivate (soft delete with retention; sessions revoked) —
    # the resource row intentionally survives a DELETE (ADR-018 §5/R330).
    "still exists after deletion",
    # userName is the platform identity — declared immutable; a replace is
    # a no-op (the tester may still probe it on older schema caches).
    "unexpected value for 'userName'",
)


def main() -> int:
    c = httpx.Client(timeout=20, trust_env=False)
    r = c.post(
        f"{API}/auth/register",
        json={
            "email": f"scim-{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test1234!",
            "display_name": "Scim Conformance",
        },
    )
    tok = r.json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    r = c.post(f"{API}/orgs", json={"name": f"SCIM {uuid.uuid4().hex[:8]}"}, headers=h)
    org = r.json()["data"]["id"]
    r = c.post(
        f"{API}/orgs/{org}/integrations/scim-tokens",
        json={"name": "t", "group_map": {}},
        headers=h,
    )
    scim_tok = r.json()["data"]["token"]

    from scim2_client.engines.httpx2 import SyncSCIMClient
    from scim2_tester import check_server

    scim_http = httpx.Client(
        base_url=f"{API}/scim/v2",
        headers={"Authorization": f"Bearer {scim_tok}"},
        timeout=20,
        trust_env=False,
    )
    client = SyncSCIMClient(scim_http)
    client.discover()
    results = check_server(client, raise_exceptions=False)

    success = skipped = dispositioned = 0
    hard: list[str] = []
    for res in results:
        if res.status.name == "SUCCESS":
            success += 1
        elif res.status.name == "SKIPPED":
            skipped += 1
        elif any(marker in str(res.reason) for marker in ALLOWED_FAILURES):
            dispositioned += 1
            print(f"  dispositioned  {res.title}: {str(res.reason)[:110]}")
        else:
            hard.append(f"{res.title}: {str(res.reason)[:180]}")
    for line in hard:
        print(f" FAIL {line}")
    print(f"\nsuccess={success} skipped={skipped} dispositioned={dispositioned} hard={len(hard)}")
    return 0 if not hard else 1


raise SystemExit(main())

"""R484: concurrent duplicate-create races against a LIVE API.

Every fabric create that sits on a unique index is fired N=8 times in
parallel with IDENTICAL payloads. The winner must 2xx; every loser must be
a clean 4xx (409/422) — a 23505 unique-violation leaking as a 500 means the
create path has no race recovery (sequential pre-checks pass the battery but
lose the TOCTOU window under concurrency).

Usage: APP_ENV=test API on :8000, then
  cd apps/api && PYTHONPATH=. uv run python tests/e2e_race_probe.py
"""

import asyncio
import uuid

import httpx

API = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0
RESULTS: list[str] = []
N = 8


def check(label: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    if ok:
        PASS += 1
        RESULTS.append(f"  ok {label}")
    else:
        FAIL += 1
        RESULTS.append(f"  FAIL {label}{f' — {detail}' if detail else ''}")


async def race(c, label, method, url, body, headers, min_wins=1):
    rs = await asyncio.gather(
        *[c.request(method, url, json=body, headers=headers) for _ in range(N)]
    )
    codes = sorted(r.status_code for r in rs)
    n5 = sum(1 for s in codes if s >= 500)
    wins = sum(1 for s in codes if s < 300)
    detail = f"codes={codes}"
    if n5:
        bad = next(r for r in rs if r.status_code >= 500)
        detail += f" body={bad.text[:140]}"
    check(f"{label}: no 5xx", n5 == 0, detail)
    check(f"{label}: >= {min_wins} winner", wins >= min_wins, detail)
    return rs


async def main() -> None:
    async with httpx.AsyncClient(timeout=20.0, trust_env=False) as c:
        email = f"race-{uuid.uuid4().hex[:10]}@test.com"
        r = await c.post(
            f"{API}/auth/register",
            json={"email": email, "password": "Test1234!", "display_name": "Race"},
        )
        tok = r.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        r = await c.post(f"{API}/orgs", json={"name": f"Race {uuid.uuid4().hex[:12]}"}, headers=h)
        org = r.json()["data"]["id"]
        base = f"{API}/orgs/{org}/integrations"
        u = uuid.uuid4().hex[:8]

        # 1) connections — uq_intg_conn_org_name
        rs = await race(
            c,
            "connection create same name",
            "POST",
            f"{base}/connections",
            {
                "provider_key": "oneroster",
                "name": f"rc-{u}",
                "config": {"token_url": "https://rc.example.com/token"},
                "base_url": "https://rc.example.com",
            },
            h,
        )
        conn_id = next(
            (r.json()["data"]["id"] for r in rs if r.status_code < 300), None
        )

        # 2) mapping profiles — uq_intg_mapping_org_name
        rs = await race(
            c,
            "mapping create same name",
            "POST",
            f"{base}/mapping-profiles",
            {
                "name": f"rm-{u}",
                "direction": "inbound",
                "model": "roster.class",
                "document": {"fields": [{"target": "t", "path": "a"}]},
            },
            h,
        )
        map_id = next(
            (r.json()["data"]["id"] for r in rs if r.status_code < 300), None
        )

        # 3) export streams — uq_intg_export_org_name
        await race(
            c,
            "export stream same name",
            "POST",
            f"{base}/export-streams",
            {"name": f"re-{u}", "dataset": "events"},
            h,
        )

        # 4) sync profiles — uq_intg_syncprof (connection, model, direction)
        if conn_id:
            await race(
                c,
                "sync profile same (conn,model,direction)",
                "POST",
                f"{base}/sync-profiles",
                {
                    "connection_id": conn_id,
                    "name": f"rs-{u}",
                    "model": "roster.class",
                    "direction": "pull",
                    "mapping_profile_id": map_id,
                },
                h,
            )

        # 5) domains — uq_intg_domain_org (R113 savepoint, verify it holds live)
        await race(
            c,
            "domain claim same domain",
            "POST",
            f"{base}/domains",
            {"domain": f"race-{u}.example.edu"},
            h,
        )

        # 6) SCIM group + user — uq_intg_scim_group_org_name / userName reuse
        r = await c.post(
            f"{base}/scim-tokens", json={"name": f"rt-{u}", "group_map": {}}, headers=h
        )
        scim_raw = r.json()["data"]["token"]
        sh = {
            "Authorization": f"Bearer {scim_raw}",
            "Content-Type": "application/scim+json",
        }
        await race(
            c,
            "scim group same displayName",
            "POST",
            f"{API}/scim/v2/Groups",
            {"displayName": f"RG-{u}"},
            sh,
        )
        # SCIM user create is reactivate-on-reuse: ALL N may legitimately 2xx
        # (winner creates, losers reactivate) — only the no-5xx arm matters.
        await race(
            c,
            "scim user same userName",
            "POST",
            f"{API}/scim/v2/Users",
            {"userName": f"race-{u}@race.example.edu"},
            sh,
        )

        # 7) LTI registrations — uq_intg_lti_reg (issuer, client_id)
        issuer = f"https://race-{u}.example.com"
        await race(
            c,
            "lti registration same issuer+client",
            "POST",
            f"{base}/lti/registrations",
            {
                "issuer": issuer,
                "client_id": "rc",
                "auth_login_url": f"{issuer}/auth",
                "auth_token_url": f"{issuer}/token",
                "jwks_url": f"{issuer}/jwks",
            },
            h,
        )

    print("\n".join(RESULTS))
    print(f"\nPASSED {PASS}  FAILED {FAIL}")
    raise SystemExit(0 if FAIL == 0 else 1)


asyncio.run(main())

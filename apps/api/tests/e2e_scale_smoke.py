"""Scale smoke (R329): the fabric at a realistic directory size, live HTTP.

Not a benchmark — a BOUNDS test: 300 SCIM users created concurrently, the
whole directory paged through SQL-side pagination, an eq-filter point
lookup, and a 50-user bulk deactivate, each under a generous wall-clock
bound. Catches accidental O(N) point-SELECT regressions (the R218 class)
and pagination breakage at sizes the unit suites never reach.

Usage: api on :8443 (APP_ENV=test), then
  E2E_INTG_API=http://localhost:8443/api/v1 PYTHONPATH=. \
      uv run python tests/e2e_scale_smoke.py
"""

import asyncio
import os
import time
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8443/api/v1")
N_USERS = 300
PASS = 0
FAIL = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f" FAIL {label}: {detail[:200]}")


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0, trust_env=False) as c:
        email = f"scale-{uuid.uuid4().hex[:10]}@test.com"
        r = await c.post(
            f"{API}/auth/register",
            json={"email": email, "password": "Test1234!", "display_name": "Scale"},
        )
        check("register", r.status_code == 201, r.text)
        tok = r.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        r = await c.post(f"{API}/orgs", json={"name": f"Scale {uuid.uuid4().hex[:6]}"}, headers=h)
        org = r.json()["data"]["id"]
        base = f"{API}/orgs/{org}/integrations"

        r = await c.post(f"{base}/scim-tokens", json={"name": "scale", "group_map": {}}, headers=h)
        check("scim token minted", r.status_code == 201, r.text)
        raw = r.json()["data"]["token"]
        sh = {"Authorization": f"Bearer {raw}", "Content-Type": "application/scim+json"}
        scim = f"{API}/scim/v2"

        # ── create 300 users, 10-way concurrent ──
        t0 = time.monotonic()
        sem = asyncio.Semaphore(10)
        dom = f"scale-{uuid.uuid4().hex[:8]}.example.edu"

        async def mk(i: int) -> int:
            async with sem:
                rr = await c.post(
                    f"{scim}/Users",
                    json={
                        "userName": f"u{i}-{uuid.uuid4().hex[:6]}@{dom}",
                        "displayName": f"Scale User {i}",
                    },
                    headers=sh,
                )
                return rr.status_code

        codes = await asyncio.gather(*[mk(i) for i in range(N_USERS)])
        created = sum(1 for s in codes if s == 201)
        dt_create = time.monotonic() - t0
        check(f"{N_USERS} users created", created == N_USERS, f"created={created}")
        check("create wall-clock bound (<60s)", dt_create < 60, f"{dt_create:.1f}s")

        # ── page through the whole directory ──
        t0 = time.monotonic()
        seen = 0
        start = 1
        pages = 0
        while True:
            rr = await c.get(
                f"{scim}/Users", params={"startIndex": start, "count": 100}, headers=sh
            )
            body = rr.json()
            got = len(body.get("Resources", []))
            seen += got
            pages += 1
            if got < 100 or pages > 20:
                break
            start += got
        dt_page = time.monotonic() - t0
        check("directory pages to completion", seen >= N_USERS, f"seen={seen}")
        check("paging wall-clock bound (<15s)", dt_page < 15, f"{dt_page:.1f}s")
        check("totalResults consistent", body.get("totalResults", 0) >= N_USERS)

        # ── eq-filter point lookup stays fast at size ──
        rr = await c.get(f"{scim}/Users", params={"count": 1}, headers=sh)
        uname = rr.json()["Resources"][0]["userName"]
        t0 = time.monotonic()
        rr = await c.get(f"{scim}/Users", params={"filter": f'userName eq "{uname}"'}, headers=sh)
        dt_f = time.monotonic() - t0
        check("eq filter finds exactly one", rr.json().get("totalResults") == 1, rr.text[:120])
        check("filter wall-clock bound (<2s)", dt_f < 2, f"{dt_f:.2f}s")

        # ── bulk deactivate 50 ──
        rr = await c.get(f"{scim}/Users", params={"count": 50}, headers=sh)
        ids = [res["id"] for res in rr.json()["Resources"]]
        ops = [
            {
                "method": "PATCH",
                "path": f"/Users/{uid}",
                "data": {"Operations": [{"op": "replace", "path": "active", "value": False}]},
            }
            for uid in ids
        ]
        t0 = time.monotonic()
        rr = await c.post(
            f"{scim}/Bulk",
            json={
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                "Operations": ops,
            },
            headers=sh,
        )
        dt_b = time.monotonic() - t0
        st = [o["status"] for o in rr.json().get("Operations", [])]
        check(
            "bulk deactivate 50 all 200",
            st and all(s == "200" for s in st),
            f"{rr.status_code} {st[:5]}",
        )
        check("bulk wall-clock bound (<20s)", dt_b < 20, f"{dt_b:.1f}s")

    print(f"\nPASS={PASS} FAIL={FAIL}")
    raise SystemExit(0 if FAIL == 0 else 1)


asyncio.run(main())

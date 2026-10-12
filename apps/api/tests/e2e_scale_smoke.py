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
        rr = await c.get(f"{scim}/Users", params={"count": 51}, headers=sh)
        # R330: the admin who minted the token is in the directory too —
        # deactivating them revokes our own session mid-smoke.
        ids = [res["id"] for res in rr.json()["Resources"] if res["userName"] != email][:50]
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

        # ── import at size: 500-row CSV upload -> preview -> commit ──
        idom = f"imp-{uuid.uuid4().hex[:8]}.example.edu"
        csv_body = "email,display_name,role\n" + "\n".join(
            f"i{i}-{uuid.uuid4().hex[:4]}@{idom},Import {i},student" for i in range(500)
        )
        t0 = time.monotonic()
        rr = await c.post(
            f"{base}/imports",
            headers=h,
            data={"kind": "users", "mode": "partial",
                  "idempotency_key": f"scale-{uuid.uuid4().hex[:10]}"},
            files={"file": ("users.csv", csv_body.encode(), "text/csv")},
        )
        dt_prev = time.monotonic() - t0
        ok_prev = rr.status_code in (200, 201) and rr.json()["data"]["dry_stats"]["valid"] == 500
        check("500-row CSV previews clean", ok_prev, rr.text[:160])
        check("preview wall-clock bound (<30s)", dt_prev < 30, f"{dt_prev:.1f}s")
        if ok_prev:
            job_id = rr.json()["data"]["id"]
            t0 = time.monotonic()
            rr = await c.post(
                f"{base}/imports/{job_id}/commit", headers=h,
                timeout=httpx.Timeout(180.0),
            )
            dt_commit = time.monotonic() - t0
            applied = rr.json().get("data", {}).get("stats", {}).get("applied", 0)
            check("500 rows committed", rr.status_code == 200 and applied == 500,
                  f"{rr.status_code} {rr.text[:140]}")
            check("commit wall-clock bound (<60s)", dt_commit < 60, f"{dt_commit:.1f}s")
            rr = await c.get(f"{API}/orgs/{org}/members", params={"limit": 1}, headers=h)
            total_members = rr.json().get("meta", {}).get("total", 0)
            check("member count reflects the import", total_members >= 500,
                  f"total={total_members} {rr.text[:100]}")

        # ── mesh at size: 200 events fan out to 2 subscriptions ──
        sink_payloads: list[bytes] = []

        async def handle(reader, writer):
            import contextlib

            data = await reader.read(65536)
            with contextlib.suppress(Exception):
                sink_payloads.append(data.split(b"\r\n\r\n", 1)[1])
            writer.write(b"HTTP/1.1 200 OK\r\ncontent-length: 0\r\nconnection: close\r\n\r\n")
            await writer.drain()
            writer.close()

        server = await asyncio.start_server(handle, "127.0.0.1", 8080)
        try:
            for name in ("a", "b"):
                rr = await c.post(
                    f"{API}/orgs/{org}/webhooks",
                    json={"url": f"http://127.0.0.1:8080/scale-{name}",
                          "events": ["com.openskill.project.approved.v1"]},
                    headers=h,
                )
                check(f"sub {name} created", rr.status_code == 201, rr.text[:120])

            from app.controlplane.worker import process_outbox_once
            from app.core.database import AsyncSessionLocal, engine
            from app.integrations.facade import emit_event

            await engine.dispose(close=False)
            t0 = time.monotonic()
            async with AsyncSessionLocal() as db:
                for i in range(200):
                    await emit_event(db, org, "project.approved",
                                     subject=f"scale-{i}", data={"i": i})
                await db.commit()
            dt_emit = time.monotonic() - t0
            check("200 events emitted (<30s)", dt_emit < 30, f"{dt_emit:.1f}s")

            t0 = time.monotonic()
            async with AsyncSessionLocal() as db:
                for _ in range(400):
                    n = await process_outbox_once(
                        db, topics=["intg.event.created", "intg.delivery.attempt"]
                    )
                    if n == 0:
                        break
            dt_drive = time.monotonic() - t0
            check("outbox drained (<90s)", dt_drive < 90, f"{dt_drive:.1f}s")
            check(
                "all 400 deliveries landed on the sink",
                len(sink_payloads) >= 400,
                f"got={len(sink_payloads)}",
            )
            rr = await c.get(f"{API}/orgs/{org}/integrations/subscription-stats", headers=h)
            stats = rr.json().get("data") if rr.status_code == 200 else None
            total_ok = (
                sum(v.get("succeeded", 0) for v in stats.values()) if isinstance(stats, dict) else -1
            )
            check(
                "stats report >=400 succeeded",
                total_ok >= 400,
                f"status={rr.status_code} stats={str(stats)[:140]}",
            )
        finally:
            server.close()
            await server.wait_closed()

    print(f"\nPASS={PASS} FAIL={FAIL}")
    raise SystemExit(0 if FAIL == 0 else 1)


asyncio.run(main())

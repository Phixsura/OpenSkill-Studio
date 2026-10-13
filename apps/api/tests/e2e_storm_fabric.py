"""Concurrency storm over the fabric admin surface (R354).

20 coroutines × ~15 rounds of mixed, overlapping admin CRUD inside ONE
org (create/patch/delete connections, streams, profiles, tokens, domains,
webhooks; trigger+cancel runs) — the races suite proves specific locks;
this proves the SURFACE: under genuinely interleaved load the API answers
only 2xx/4xx (no 5xx, no deadlock-induced hangs) and the terminal state
is consistent (caps respected, no orphan live runs).

Usage: api on :8443 (APP_ENV=test), then
  E2E_INTG_API=http://localhost:8443/api/v1 PYTHONPATH=. \
      uv run python tests/e2e_storm_fabric.py
"""

import asyncio
import os
import random
import time
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8443/api/v1")
SEED = int(os.environ.get("STORM_SEED", "17"))
WORKERS = 20
ROUNDS = 15
PASS = 0
FAIL = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f" FAIL {label}: {detail[:220]}")


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0, trust_env=False) as c:
        email = f"storm-{uuid.uuid4().hex[:10]}@test.com"
        r = await c.post(
            f"{API}/auth/register",
            json={"email": email, "password": "Test1234!", "display_name": "Storm"},
        )
        tok = r.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        r = await c.post(f"{API}/orgs", json={"name": f"Storm {uuid.uuid4().hex[:6]}"}, headers=h)
        org = r.json()["data"]["id"]
        base = f"{API}/orgs/{org}/integrations"

        status_5xx: list[str] = []
        shared_hooks: list[str] = []  # R401: rotation-race target
        _run_uid = uuid.uuid4().hex[:6]  # R402: per-run resource namespace
        slowest = 0.0
        lat: list[float] = []  # every request's wall time, for percentiles

        async def req(method, url, **kw):
            nonlocal slowest
            t0 = time.monotonic()
            rr = await c.request(method, url, headers=h, **kw)
            dt = time.monotonic() - t0
            slowest = max(slowest, dt)
            lat.append(dt)
            if rr.status_code >= 500:
                status_5xx.append(f"{method} {url[-60:]} -> {rr.status_code} {rr.text[:100]}")
            return rr

        async def worker(wid: int):
            rng = random.Random(SEED * 1000 + wid)
            my_conns: list[str] = []
            my_streams: list[str] = []
            my_profiles: list[str] = []
            for i in range(ROUNDS):
                op = rng.randrange(10)
                # run-unique prefix: a seeded rng regenerates identical tags
                # every run, which left cross-run duplicate pending domains in
                # the dev DB (R402 cruft class). _run_uid makes each storm's
                # resources globally unique.
                tag = f"{_run_uid}w{wid}r{i}-{rng.randrange(9999)}"
                if op == 0:
                    rr = await req(
                        "POST",
                        f"{base}/connections",
                        json={
                            "provider_key": "generic_rest",
                            "name": f"c-{tag}",
                            "config": {},
                            "base_url": "https://x.example.com",
                        },
                    )
                    if rr.status_code == 201:
                        my_conns.append(rr.json()["data"]["id"])
                elif op == 1 and my_conns:
                    await req(
                        "PATCH",
                        f"{base}/connections/{rng.choice(my_conns)}",
                        json={"name": f"c-{tag}"},
                    )
                elif op == 2 and my_conns:
                    cid = my_conns.pop()
                    await req("DELETE", f"{base}/connections/{cid}")
                elif op == 3:
                    rr = await req(
                        "POST",
                        f"{base}/export-streams",
                        json={"name": f"s-{tag}", "dataset": "events"},
                    )
                    if rr.status_code == 201:
                        my_streams.append(rr.json()["data"]["id"])
                elif op == 4 and my_streams:
                    await req(
                        "PATCH",
                        f"{base}/export-streams/{rng.choice(my_streams)}",
                        json={"enabled": bool(rng.randrange(2))},
                    )
                elif op == 5:
                    await req(
                        "POST", f"{base}/scim-tokens", json={"name": f"t-{tag}", "group_map": {}}
                    )
                elif op == 6:
                    await req("POST", f"{base}/domains", json={"domain": f"{tag}.example.edu"})
                elif op == 7:
                    rr = await req(
                        "POST",
                        f"{API}/orgs/{org}/webhooks",
                        json={
                            "url": f"https://sink.example.com/{tag}",
                            "events": ["com.openskill.project.approved.v1"],
                        },
                    )
                    # R401: all workers rotate the SAME shared webhook —
                    # concurrent rotations must serialize on the row lock
                    # (chained-prev race), never 5xx.
                    if rr.status_code == 201:
                        shared_hooks.append(rr.json()["data"]["id"])
                    if shared_hooks:
                        await req(
                            "POST",
                            f"{API}/orgs/{org}/webhooks/{shared_hooks[0]}/rotate-secret",
                        )
                elif op == 8 and my_conns:
                    rr = await req(
                        "POST",
                        f"{base}/sync-profiles",
                        json={
                            "connection_id": rng.choice(my_conns),
                            "name": f"p-{tag}",
                            "model": "roster.class",
                            "direction": "pull",
                            "mapping_profile_id": None,
                        },
                    )
                    if rr.status_code == 201:
                        my_profiles.append(rr.json()["data"]["id"])
                else:
                    if my_profiles:
                        pid = rng.choice(my_profiles)
                        rr = await req("POST", f"{base}/sync-profiles/{pid}/run")
                        if rr.status_code in (200, 201, 202):
                            rid = rr.json()["data"]["id"]
                            await req("POST", f"{base}/sync-runs/{rid}/cancel")

        t0 = time.monotonic()
        await asyncio.gather(*[worker(w) for w in range(WORKERS)])
        dt = time.monotonic() - t0

        check(
            f"zero 5xx across the storm ({WORKERS}x{ROUNDS})",
            not status_5xx,
            " | ".join(status_5xx[:3]),
        )
        check("storm wall-clock bound (<180s)", dt < 180, f"{dt:.1f}s")
        check("no request exceeded 20s (deadlock guard)", slowest < 20, f"slowest={slowest:.1f}s")
        lat.sort()
        p = lambda q: lat[min(len(lat) - 1, int(len(lat) * q))] if lat else 0.0  # noqa: E731
        print(
            f"  latency n={len(lat)} p50={p(0.50) * 1000:.0f}ms "
            f"p95={p(0.95) * 1000:.0f}ms p99={p(0.99) * 1000:.0f}ms max={slowest * 1000:.0f}ms"
        )
        # SLO under a 20-worker storm on a loaded dev box: median under 1s,
        # p95 under 5s. A regression here is a lock/N+1 smell even when
        # nothing 5xxs.
        check("storm p50 < 1s", p(0.50) < 1.0, f"p50={p(0.50):.2f}s")
        check("storm p95 < 5s", p(0.95) < 5.0, f"p95={p(0.95):.2f}s")

        # terminal consistency: caps respected, no live runs left
        rr = await c.get(f"{base}/connections", headers=h)
        n_conns = len(rr.json()["data"])
        check("connection cap respected", n_conns <= 20, f"n={n_conns}")
        rr = await c.get(f"{base}/export-streams", headers=h)
        check("stream cap respected", len(rr.json()["data"]) <= 20, rr.text[:80])
        rr = await c.get(f"{base}/sync-runs", headers=h)
        live = [x for x in rr.json()["data"] if x["status"] in ("queued", "running")]
        check("no orphan live runs", not live, str(live)[:120])

    print(f"\nseed={SEED} PASS={PASS} FAIL={FAIL}")
    raise SystemExit(0 if FAIL == 0 else 1)


asyncio.run(main())

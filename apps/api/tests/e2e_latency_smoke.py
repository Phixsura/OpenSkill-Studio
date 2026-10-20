"""R548: latency smoke over the hot fabric read endpoints (live API).

Not a benchmark — a REGRESSION TRIPWIRE: p95 on warmed hot reads must stay
under a deliberately generous local ceiling (750ms). Numbers are printed so
each run leaves a baseline in the logs.

Usage: APP_ENV=test API on :8443, then
  E2E_INTG_API=http://localhost:8443/api/v1 PYTHONPATH=. \
      uv run python tests/e2e_latency_smoke.py
"""

import asyncio
import os
import statistics
import time
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8443/api/v1")
N = 40
CEILING_MS = 750.0


async def main() -> int:
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        r = await c.post(
            "/auth/register",
            json={
                "email": f"lat-{uuid.uuid4().hex[:10]}@test.com",
                "password": "Test1234!",
                "display_name": "Latency Smoke",
            },
        )
        h = {"Authorization": f"Bearer {r.json()['access_token']}"}
        r = await c.post("/orgs", json={"name": f"Lat {uuid.uuid4().hex[:8]}"}, headers=h)
        org = r.json()["data"]["id"]
        base = f"/orgs/{org}/integrations"

        targets = [
            ("health", "/health", {}),
            ("providers", f"{base}/providers", h),
            ("connections", f"{base}/connections", h),
            ("events list", f"{base}/events", h),
            ("event catalog", f"{base}/event-catalog", h),
            ("model catalog", f"{base}/models", h),
            ("health summary", f"{base}/health", h),
        ]
        failed = 0
        for name, path, headers in targets:
            # warm once (connection + caches), then measure serially
            resp = await c.get(path, headers=headers)
            if resp.status_code != 200:
                print(f" FAIL {name}: warmup status {resp.status_code}")
                failed += 1
                continue
            samples = []
            for _ in range(N):
                t0 = time.perf_counter()
                resp = await c.get(path, headers=headers)
                samples.append((time.perf_counter() - t0) * 1000)
                if resp.status_code != 200:
                    failed += 1
                    print(f" FAIL {name}: status {resp.status_code} mid-run")
                    break
            samples.sort()
            p50 = statistics.median(samples)
            p95 = samples[int(len(samples) * 0.95) - 1]
            ok = p95 <= CEILING_MS
            print(
                f"  {'ok  ' if ok else 'FAIL'} {name:<16} p50={p50:7.1f}ms  p95={p95:7.1f}ms  n={len(samples)}"
            )
            if not ok:
                failed += 1
    print(f"\n{'PASS' if failed == 0 else 'FAIL'} (ceiling p95 <= {CEILING_MS:.0f}ms)")
    return 0 if failed == 0 else 1


raise SystemExit(asyncio.run(main()))

# ruff: noqa: SIM115, SIM105, BLE001, S603, S607
"""R404: HTTP-layer idempotency-race drill. Fire K TRULY CONCURRENT import
uploads with the SAME idempotency_key against a live server and assert the
unique-index + savepoint recovery (R111 class) yields exactly ONE job id —
no 5xx, no duplicate jobs. The in-process DB test proves the service; this
proves the full ASGI stack under real socket concurrency.

Run from apps/api with infra up:  uv run python tests/drills/idempotency_drill.py
"""

import asyncio
import os
import signal
import subprocess
import sys
import time
import urllib.request as ur
import uuid
from pathlib import Path

API_DIR = str(Path(__file__).resolve().parents[2])
TMP = str(Path(API_DIR) / ".drill-logs")
Path(TMP).mkdir(exist_ok=True)
ur.install_opener(ur.build_opener(ur.ProxyHandler({})))  # R367

subprocess.run(["bash", "-c", "lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true"])
time.sleep(0.5)
env = dict(os.environ, APP_ENV="test", PYTHONPATH=".")
api = subprocess.Popen(
    [
        "uv",
        "run",
        "uvicorn",
        "app.main:app",
        "--no-server-header",
        "--port",
        "8443",
        "--workers",
        "1",
    ],
    cwd=API_DIR,
    stdout=open(f"{TMP}/uvicorn_idem.log", "w"),
    stderr=subprocess.STDOUT,
    env=env,
    start_new_session=True,
)


async def main():
    import httpx

    for _ in range(60):
        try:
            ur.urlopen("http://localhost:8443/api/v1/health", timeout=2)
            break
        except Exception:
            time.sleep(1)

    async with httpx.AsyncClient(timeout=60, trust_env=False) as c:
        r = await c.post(
            "http://localhost:8443/api/v1/auth/register",
            json={
                "email": f"idem-{uuid.uuid4().hex[:8]}@test.com",
                "password": "Test1234!",
                "display_name": "Idem Drill",
            },
        )
        tok = r.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        r = await c.post(
            "http://localhost:8443/api/v1/orgs",
            json={"name": f"ID {uuid.uuid4().hex[:5]}"},
            headers=h,
        )
        org = r.json()["data"]["id"]
        base = f"http://localhost:8443/api/v1/orgs/{org}/integrations"

        key = f"idem-{uuid.uuid4().hex}"
        csv = b"email,display_name,role\nidem@x.com,Idem User,student\n"

        async def upload():
            return await c.post(
                f"{base}/imports",
                data={"kind": "users", "mode": "partial", "idempotency_key": key},
                files={"file": ("a.csv", csv, "text/csv")},
                headers=h,
            )

        n_parallel = 12
        results = await asyncio.gather(
            *[upload() for _ in range(n_parallel)], return_exceptions=True
        )
        statuses, ids, errs = [], set(), 0
        for r in results:
            if isinstance(r, Exception):
                errs += 1
                continue
            statuses.append(r.status_code)
            if r.status_code >= 500:
                errs += 1
            if r.status_code in (200, 201):
                ids.add(r.json()["data"]["id"])

        print(f"statuses: {sorted(statuses)}")
        print(f"distinct job ids: {len(ids)}  5xx/exc: {errs}")
        ok = errs == 0 and len(ids) == 1
        print("DRILL", "OK" if ok else f"FAIL (ids={len(ids)} errs={errs})")
        return 0 if ok else 1


try:
    sys.exit(asyncio.run(main()))
finally:
    os.killpg(api.pid, signal.SIGKILL)

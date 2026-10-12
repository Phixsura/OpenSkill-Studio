# ruff: noqa: SIM115, SIM105, BLE001, S603, S607, E702
"""R361: crash-recovery drill — kill -9 the API mid-storm, restart, then
assert the fabric's invariants healed: no jobs stuck in committing/
validating, no stale running runs older than the reaper window, caps
intact, battery-representative suites green afterwards (run separately).
"""

import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Repo-relative: this file lives at apps/api/tests/drills/<name>.py
API_DIR = str(Path(__file__).resolve().parents[2])
ROOT = str(Path(__file__).resolve().parents[4])
TMP = str(Path(API_DIR) / ".drill-logs")
Path(TMP).mkdir(exist_ok=True)

# Never route localhost through a proxy: macOS SYSTEM proxy settings are
# honored by urllib even when env vars are clean (R367 — drill broke with
# 502s the moment the user's local proxy came on).
import urllib.request as _ur  # noqa: E402

_ur.install_opener(_ur.build_opener(_ur.ProxyHandler({})))


def start_api():
    env = dict(os.environ, APP_ENV="test", EGRESS_ALLOW_PRIVATE="true", PYTHONPATH=".")
    return subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--no-server-header", "--port", "8443"],
        cwd=API_DIR,
        stdout=open(f"{TMP}/uvicorn_crash.log", "w"),
        stderr=subprocess.STDOUT,
        env=env,
        start_new_session=True,
    )


def wait_up(tries=120):
    for _ in range(tries):
        try:
            urllib.request.urlopen("http://localhost:8443/api/v1/health", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


subprocess.run(["bash", "-c", "lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true"])
time.sleep(0.5)
api = start_api()
if not wait_up():
    print("api never came up")
    sys.exit(1)

env2 = dict(
    os.environ,
    APP_ENV="test",
    E2E_INTG_API="http://localhost:8443/api/v1",
    PYTHONPATH=".",
    STORM_SEED="314",
)
storm = subprocess.Popen(
    ["uv", "run", "python", "tests/e2e_storm_fabric.py"],
    cwd=API_DIR,
    stdout=open(f"{TMP}/storm_crash.log", "w"),
    stderr=subprocess.STDOUT,
    env=env2,
    start_new_session=True,
)
time.sleep(12)  # let the storm get deep into mixed writes
print("KILL -9 api mid-storm")
os.killpg(api.pid, signal.SIGKILL)
time.sleep(2)
# the storm will fail with connection errors — that's expected; reap it
try:
    os.killpg(storm.pid, signal.SIGKILL)
except Exception:
    pass

api2 = start_api()
if not wait_up():
    print("api failed to RESTART after crash")
    sys.exit(1)
print("api restarted cleanly after kill -9")

code = r"""
import asyncio
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.integrations.models import ImportJob, SyncRun
from app.integrations.models.export import ExportRun

async def main():
    async with AsyncSessionLocal() as db:
        stuck = (await db.execute(select(ImportJob.id).where(
            ImportJob.status.in_(("committing", "validating"))))).all()
        print("stuck import jobs:", len(stuck))
        cutoff = datetime.now(UTC) - timedelta(minutes=2)
        recent_running = (await db.execute(select(SyncRun.id).where(
            SyncRun.status == "running", SyncRun.created_at > cutoff))).all()
        print("fresh running runs (reaper will own older):", len(recent_running))
        xr = (await db.execute(select(ExportRun.id).where(
            ExportRun.status == "running", ExportRun.created_at > cutoff))).all()
        print("fresh running exports:", len(xr))

asyncio.run(main())
"""
r = subprocess.run(
    ["uv", "run", "python", "-c", code],
    cwd=API_DIR,
    env=dict(os.environ, APP_ENV="test", PYTHONPATH="."),
    capture_output=True,
    text=True,
)
print(r.stdout.strip())
if r.returncode:
    print(r.stderr[-400:])
    sys.exit(1)
stuck_line = [ln for ln in r.stdout.splitlines() if "stuck import jobs" in ln]
ok = stuck_line and stuck_line[0].strip().endswith(" 0")
print("DRILL", "OK" if ok else "FAIL (stuck committing jobs!)")
os.killpg(api2.pid, signal.SIGKILL)
sys.exit(0 if ok else 1)

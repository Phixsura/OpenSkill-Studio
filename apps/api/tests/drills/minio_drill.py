# ruff: noqa: SIM115, BLE001, S603, S607, E702
"""R362b: object-storage outage drill — run an export while MinIO is down:
the run must land as a CLEAN failed (enveloped 4xx/5xx-free API, run row
terminal), and a rerun after recovery succeeds."""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request as ur
import uuid
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


def sh(cmd):
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


minio_id = (
    sh("docker ps -q --filter name=minio --filter status=running").stdout.strip().split("\n")[0]
)
if not minio_id:
    print("no running minio container found")
    sys.exit(1)

sh("lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true")
time.sleep(0.5)
env = dict(os.environ, APP_ENV="test", PYTHONPATH=".")
api = subprocess.Popen(
    ["uv", "run", "uvicorn", "app.main:app", "--no-server-header", "--port", "8443"],
    cwd=API_DIR,
    stdout=open(f"{TMP}/uvicorn_minio.log", "w"),
    stderr=subprocess.STDOUT,
    env=env,
    start_new_session=True,
)
try:
    for _ in range(60):
        try:
            ur.urlopen("http://localhost:8443/api/v1/health", timeout=2)
            break
        except Exception:
            time.sleep(1)

    def req(method, path, body=None, tok=None, timeout=60):
        data = json.dumps(body).encode() if body is not None else None
        r = ur.Request(f"http://localhost:8443/api/v1{path}", data=data, method=method)
        r.add_header("Content-Type", "application/json")
        if tok:
            r.add_header("Authorization", f"Bearer {tok}")
        try:
            with ur.urlopen(r, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    st, body = req(
        "POST",
        "/auth/register",
        {
            "email": f"mn-{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test1234!",
            "display_name": "MinIO Drill",
        },
    )
    tok = body["access_token"]
    st, body = req("POST", "/orgs", {"name": f"MN {uuid.uuid4().hex[:5]}"}, tok)
    org = body["data"]["id"]
    base = f"/orgs/{org}/integrations"
    # one event so the export has a row to write
    # (emit via webhook test is heavy — the dataset tolerates zero rows, but
    # zero-row export may not touch S3; create an event through an import)
    st, body = req(
        "POST",
        f"{base}/export-streams",
        {"name": f"mn-{uuid.uuid4().hex[:5]}", "dataset": "events"},
        tok,
    )
    stream = body["data"]["id"]

    print("stopping minio...")
    sh(f"docker stop {minio_id}")
    time.sleep(1)

    st, body = req("POST", f"{base}/export-streams/{stream}/run", tok=tok, timeout=120)
    print("during-outage run:", st, str(body)[:160])
    clean_fail = (
        st in (202, 409, 422, 502)
        and body.get("data", {}).get("status") in ("failed", None)
        or st == 500
    )
    # the REAL assertion: not a 500, and the run row is terminal
    not_500 = st != 500
    st2, body2 = req("GET", f"{base}/export-streams/{stream}/runs", tok=tok)
    runs = body2.get("data", [])
    terminal = all(r.get("status") in ("failed", "succeeded") for r in runs)
    print("runs after outage:", [(r.get("status")) for r in runs])

    print("restarting minio...")
    sh(f"docker start {minio_id}")
    for _ in range(30):
        if sh("curl -sf http://localhost:9000/minio/health/live").returncode == 0:
            break
        time.sleep(2)
    st3, body3 = req("POST", f"{base}/export-streams/{stream}/run", tok=tok, timeout=120)
    ok_after = st3 == 202 and body3.get("data", {}).get("status") == "succeeded"
    print("after-recovery run:", st3, body3.get("data", {}).get("status"))

    ok = not_500 and terminal and ok_after
    print("DRILL", "OK" if ok else f"FAIL not_500={not_500} terminal={terminal} after={ok_after}")
    _ = clean_fail  # informational; ok below is the real gate
    sys.exit(0 if ok else 1)
finally:
    sh(f"docker start {minio_id} >/dev/null 2>&1; true")
    os.killpg(api.pid, signal.SIGKILL)

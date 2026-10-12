# ruff: noqa: SIM115, BLE001, S603, S607, E702
"""R362: Redis-outage drill — stop the redis container mid-traffic and
assert the declared fail-open behavior: the API keeps answering (rate
limiting and metering degrade gracefully, nothing 5xxs), then full
function returns when redis does."""

import os
import signal
import subprocess
import sys
import time
import urllib.request
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


redis_id = (
    sh("docker ps -q --filter name=redis --filter status=running").stdout.strip().split("\n")[0]
)
if not redis_id:
    print("no running redis container found")
    sys.exit(1)

sh("lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true")
time.sleep(0.5)
env = dict(os.environ, APP_ENV="test", PYTHONPATH=".")
api = subprocess.Popen(
    ["uv", "run", "uvicorn", "app.main:app", "--no-server-header", "--port", "8443"],
    cwd=API_DIR,
    stdout=open(f"{TMP}/uvicorn_redis.log", "w"),
    stderr=subprocess.STDOUT,
    env=env,
    start_new_session=True,
)
try:
    for _ in range(60):
        try:
            urllib.request.urlopen("http://localhost:8443/api/v1/health", timeout=2)
            break
        except Exception:
            time.sleep(1)

    import json
    import urllib.error
    import urllib.request as ur

    def req(method, path, body=None, tok=None):
        data = json.dumps(body).encode() if body is not None else None
        r = ur.Request(f"http://localhost:8443/api/v1{path}", data=data, method=method)
        r.add_header("Content-Type", "application/json")
        if tok:
            r.add_header("Authorization", f"Bearer {tok}")
        try:
            with ur.urlopen(r, timeout=20) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    st, body = req(
        "POST",
        "/auth/register",
        {
            "email": f"rd-{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test1234!",
            "display_name": "Redis Drill",
        },
    )
    assert st == 201, (st, body)
    tok = body["access_token"]
    st, body = req("POST", "/orgs", {"name": f"RD {uuid.uuid4().hex[:5]}"}, tok)
    org = body["data"]["id"]

    print("stopping redis...")
    sh(f"docker stop {redis_id}")
    time.sleep(1)

    fails = []
    for i in range(10):
        st, body = req("GET", f"/orgs/{org}/integrations/domains", tok=tok)
        if st >= 500:
            fails.append((i, st, str(body)[:100]))
        st2, body2 = req(
            "POST",
            f"/orgs/{org}/integrations/domains",
            {"domain": f"rd{i}-{uuid.uuid4().hex[:4]}.example.edu"},
            tok,
        )
        if st2 >= 500:
            fails.append(("w" + str(i), st2, str(body2)[:100]))
    print("during-outage 5xx:", fails or "none")

    print("restarting redis...")
    sh(f"docker start {redis_id}")
    time.sleep(3)
    st, _ = req("GET", f"/orgs/{org}/integrations/domains", tok=tok)
    print("after-recovery status:", st)
    ok = not fails and st == 200
    print("DRILL", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)
finally:
    sh(f"docker start {redis_id} >/dev/null 2>&1; true")
    os.killpg(api.pid, signal.SIGKILL)

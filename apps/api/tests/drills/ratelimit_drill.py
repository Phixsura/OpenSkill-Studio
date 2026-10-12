# ruff: noqa: SIM115, BLE001, S603, S607, E702
"""R366: rate-limiter ENGAGEMENT drill. Every live suite runs APP_ENV=test,
where rate limiting is skipped by design — so the 429 path had never been
exercised live. Boot the API in development mode (real redis limiter),
burst one tightly-limited route (replay-exhausted, 10/60, keyed on route
template + user), and assert: allowed responses carry X-RateLimit-*
transparency headers, the burst trips a real 429 with Retry-After, and
OTHER routes for the same user still answer (bucket is per-route)."""

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


subprocess.run(["bash", "-c", "lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true"])
time.sleep(0.5)
env = dict(os.environ, APP_ENV="development", PYTHONPATH=".")
api = subprocess.Popen(
    ["uv", "run", "uvicorn", "app.main:app", "--no-server-header", "--port", "8443"],
    cwd=API_DIR,
    stdout=open(f"{TMP}/uvicorn_rl.log", "w"),
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

    def req(method, path, body=None, tok=None):
        data = json.dumps(body).encode() if body is not None else None
        r = ur.Request(f"http://localhost:8443/api/v1{path}", data=data, method=method)
        r.add_header("Content-Type", "application/json")
        if tok:
            r.add_header("Authorization", f"Bearer {tok}")
        try:
            with ur.urlopen(r, timeout=20) as resp:
                h_ = {k.lower(): v for k, v in resp.headers.items()}
                return resp.status, h_, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            h_ = {k.lower(): v for k, v in e.headers.items()}
            return e.code, h_, json.loads(e.read() or b"{}")

    st, _, body = req(
        "POST",
        "/auth/register",
        {
            "email": f"rl-{uuid.uuid4().hex[:8]}@test.com",
            "password": "Test1234!",
            "display_name": "RateLimit Drill",
        },
    )
    assert st == 201, (st, body)
    tok = body["access_token"]
    st, _, body = req("POST", "/orgs", {"name": f"RL {uuid.uuid4().hex[:5]}"}, tok)
    assert st == 201, (st, body)
    org = body["data"]["id"]
    burst_path = f"/orgs/{org}/integrations/webhooks/{'0' * 26}/replay-exhausted"

    fails, saw_429, first_headers, statuses = [], None, None, []
    for i in range(14):  # budget 10 -> expect exactly 10 allowed, 11th = 429
        st, hdr, body = req("POST", burst_path, tok=tok)
        statuses.append(st)
        if i == 0:
            first_headers = hdr
        if st == 429:
            saw_429 = hdr
            break
        if st >= 500:
            fails.append((i, st, str(body)[:100]))

    ok_headers = (
        bool(first_headers)
        and first_headers.get("x-ratelimit-limit") == "10"
        and "x-ratelimit-remaining" in first_headers
    )
    ok_429 = (
        saw_429 is not None
        and saw_429.get("retry-after") == "60"
        and saw_429.get("x-ratelimit-remaining") == "0"
    )
    # bucket is per-route: another fabric route still answers for this user
    st2, _, _ = req("GET", f"/orgs/{org}/integrations/domains", tok=tok)
    ok_other = st2 == 200

    print("statuses:", statuses)
    print(
        "transparency headers on allowed:",
        ok_headers,
        {k: v for k, v in (first_headers or {}).items() if k.startswith("x-ratelimit")},
    )
    print(
        "429 with Retry-After:",
        ok_429,
        {k: v for k, v in (saw_429 or {}).items() if k in ("retry-after", "x-ratelimit-remaining")},
    )
    print("other route unaffected (per-route bucket):", ok_other, st2)
    ok = ok_headers and ok_429 and ok_other and not fails
    print("DRILL", "OK" if ok else f"FAIL 5xx={fails}")
    sys.exit(0 if ok else 1)
finally:
    os.killpg(api.pid, signal.SIGKILL)

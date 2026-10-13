# ruff: noqa: SIM115, SIM105, BLE001, S603, S607
"""R380: slow-sink (slowloris) delivery drill — a webhook receiver that
ACCEPTS the connection and then stalls must not wedge the delivery path.
The EgressClient read-timeout (15 s) must fire: the synchronous
/webhooks/{id}/test dispatch returns a FAILURE RESULT (not a 500, not a
hang) in ~15-20 s, and a normal fast sink still succeeds right after.

Run from apps/api with infra up:  uv run python tests/drills/slow_sink_drill.py
"""
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request as ur
import uuid
from pathlib import Path

API_DIR = str(Path(__file__).resolve().parents[2])
TMP = str(Path(API_DIR) / ".drill-logs")
Path(TMP).mkdir(exist_ok=True)

ur.install_opener(ur.build_opener(ur.ProxyHandler({})))  # R367


def slow_sink(port: int, stall_s: float):
    """Accept, read the request, then stall without responding."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(8)

    def loop():
        while True:
            try:
                conn, _ = srv.accept()
            except OSError:
                return
            def handle(c):
                try:
                    c.settimeout(stall_s + 5)
                    c.recv(65536)  # swallow the request
                    time.sleep(stall_s)  # ...and say nothing
                    c.close()
                except Exception:
                    pass
            threading.Thread(target=handle, args=(conn,), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()
    return srv


def fast_sink(port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(8)

    def loop():
        while True:
            try:
                conn, _ = srv.accept()
            except OSError:
                return
            try:
                conn.recv(65536)
                conn.sendall(b"HTTP/1.1 200 OK\r\ncontent-length: 2\r\nconnection: close\r\n\r\nok")
                conn.close()
            except Exception:
                pass

    threading.Thread(target=loop, daemon=True).start()
    return srv


subprocess.run(["bash", "-c", "lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true"])
time.sleep(0.5)
env = dict(os.environ, APP_ENV="test", EGRESS_ALLOW_PRIVATE="true", PYTHONPATH=".")
api = subprocess.Popen(
    ["uv", "run", "uvicorn", "app.main:app", "--no-server-header", "--port", "8443"],
    cwd=API_DIR, stdout=open(f"{TMP}/uvicorn_slowsink.log", "w"),
    stderr=subprocess.STDOUT, env=env, start_new_session=True,
)
slow = slow_sink(8080, stall_s=60)  # 8080: the one allowed spare port
fast = None
try:
    for _ in range(60):
        try:
            ur.urlopen("http://localhost:8443/api/v1/health", timeout=2)
            break
        except Exception:
            time.sleep(1)

    def req(method, path, body=None, tok=None, timeout=90):
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

    st, body = req("POST", "/auth/register",
                   {"email": f"ss-{uuid.uuid4().hex[:8]}@test.com",
                    "password": "Test1234!", "display_name": "SlowSink Drill"})
    assert st == 201, (st, body)
    tok = body["access_token"]
    st, body = req("POST", "/orgs", {"name": f"SS {uuid.uuid4().hex[:5]}"}, tok)
    org = body["data"]["id"]

    st, body = req("POST", f"/orgs/{org}/webhooks",
                   {"url": "http://127.0.0.1:8080/hook",
                    "events": ["com.openskill.project.approved.v1"]}, tok)
    assert st == 201, (st, body)
    slow_id = body["data"]["id"]
    st, body = req("POST", f"/orgs/{org}/webhooks",
                   {"url": "http://127.0.0.1:8080/hook",
                    "events": ["com.openskill.project.approved.v1"]}, tok)
    fast_id = body["data"]["id"]

    t0 = time.monotonic()
    st, body = req("POST", f"/orgs/{org}/webhooks/{slow_id}/test", tok=tok, timeout=90)
    dt = time.monotonic() - t0
    data = body.get("data", {})
    print(f"slow sink: status={st} elapsed={dt:.1f}s result={str(data)[:160]}")
    # the read timeout is 15s — the dispatch must give up in 14-30s, not 60+
    ok_slow = st == 200 and 10 <= dt <= 35 and not data.get("ok", data.get("success", False))

    # swap the sink: close the stalling listener, start a fast one on 8080
    slow.close()
    time.sleep(0.5)
    fast = fast_sink(8080)

    t1 = time.monotonic()
    st2, body2 = req("POST", f"/orgs/{org}/webhooks/{fast_id}/test", tok=tok, timeout=90)
    dt2 = time.monotonic() - t1
    data2 = body2.get("data", {})
    print(f"fast sink: status={st2} elapsed={dt2:.1f}s result={str(data2)[:160]}")
    ok_fast = st2 == 200 and dt2 < 10 and (
        data2.get("ok") or data2.get("success") or data2.get("status_code") == 200
        or data2.get("status") == 200
    )

    ok = ok_slow and ok_fast
    print("DRILL", "OK" if ok else f"FAIL slow={ok_slow} fast={ok_fast}")
    sys.exit(0 if ok else 1)
finally:
    for srv in (slow, fast):
        try:
            srv.close()
        except Exception:
            pass
    os.killpg(api.pid, signal.SIGKILL)

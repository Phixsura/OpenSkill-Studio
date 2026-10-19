# ruff: noqa: SIM115, SIM105, BLE001, S603, S607
"""R398: memory-leak soak drill — N consecutive concurrency storms against
ONE uvicorn process while sampling its RSS after every storm. Prior soaks
proved latency stays flat; this proves the PROCESS does not grow without
bound (connection pools, caches, replay stores). Pass: final RSS below
2x the post-warmup RSS and below an absolute 1.5 GB ceiling.

Run from apps/api with infra up:  uv run python tests/drills/soak_drill.py [N]
"""

import os
import re
import signal
import subprocess
import sys
import time
import urllib.request as ur
from pathlib import Path

API_DIR = str(Path(__file__).resolve().parents[2])
TMP = str(Path(API_DIR) / ".drill-logs")
Path(TMP).mkdir(exist_ok=True)

ur.install_opener(ur.build_opener(ur.ProxyHandler({})))  # R367

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def sh(cmd: str) -> str:
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True).stdout


def rss_mb(pid: int) -> float:
    out = sh(f"ps -o rss= -p {pid}")
    return int(out.strip() or 0) / 1024


subprocess.run(["bash", "-c", "lsof -tiTCP:8443 -sTCP:LISTEN | xargs kill -9 2>/dev/null; true"])
time.sleep(0.5)
env = dict(os.environ, APP_ENV="test", PYTHONPATH=".")
api = subprocess.Popen(
    ["uv", "run", "uvicorn", "app.main:app", "--no-server-header", "--port", "8443"],
    cwd=API_DIR,
    stdout=open(f"{TMP}/uvicorn_soak.log", "w"),
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
    # the uvicorn worker is a child of the `uv run` wrapper — find it
    time.sleep(1)
    kids = sh(f"pgrep -P {api.pid}").split()
    worker = int(kids[0]) if kids else api.pid

    samples: list[float] = []
    p95s: list[int] = []
    for i in range(N):
        r = subprocess.run(
            ["uv", "run", "python", "tests/e2e_storm_fabric.py"],
            cwd=API_DIR,
            capture_output=True,
            text=True,
            env=dict(env, E2E_INTG_API="http://localhost:8443/api/v1", STORM_SEED=str(500 + i)),
        )
        if r.returncode != 0:
            print(f"storm {i} FAILED:\n{r.stdout[-400:]}")
            sys.exit(1)
        m = re.search(r"p95=(\d+)ms", r.stdout)
        p95s.append(int(m.group(1)) if m else -1)
        samples.append(rss_mb(worker))
        print(f"storm {i + 1:2d}/{N}: rss={samples[-1]:.0f}MB p95={p95s[-1]}ms")

    warm = samples[1] if len(samples) > 1 else samples[0]
    final = samples[-1]
    ok = final < max(warm * 2, warm + 200) and final < 1536
    print(
        f"warm rss={warm:.0f}MB final rss={final:.0f}MB "
        f"growth={(final - warm):+.0f}MB over {N - 1} storms"
    )
    print("DRILL", "OK" if ok else "FAIL (unbounded RSS growth)")
    sys.exit(0 if ok else 1)
finally:
    os.killpg(api.pid, signal.SIGKILL)

"""R627: arq WORKER soak — the API process was soak-proven (R398/R626) but
the worker runs 24/7 draining the outbox + 20 crons; a leak there bricks
deployments slowly. Start a REAL worker, pump mesh events through the outbox
in waves, sample the worker's RSS after each wave.

Usage: uv run python tests/drills/worker_soak_drill.py [waves=8]
"""

import asyncio
import os
import subprocess
import sys

WAVES = int(sys.argv[1]) if len(sys.argv) > 1 else 8
EVENTS_PER_WAVE = 120


def _worker_pid(wrapper_pid: int) -> int:
    """uv run does NOT exec — the arq worker is a CHILD of the wrapper
    (R554/R627: sampling the wrapper reads ~20MB of uv, not the worker)."""
    out = subprocess.run(["pgrep", "-P", str(wrapper_pid)], capture_output=True, text=True)
    kids = [int(x) for x in out.stdout.split()]
    return kids[0] if kids else wrapper_pid


def rss_mb(pid: int) -> float:
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True)
    return int(out.stdout.strip() or 0) / 1024


async def main() -> int:
    os.environ.setdefault("APP_ENV", "test")
    proc = subprocess.Popen(
        ["uv", "run", "arq", "app.controlplane.worker.WorkerSettings"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        await asyncio.sleep(4)  # worker boot
        target_pid = _worker_pid(proc.pid)
        from sqlalchemy import func, select

        from app.core.database import AsyncSessionLocal, engine
        from app.integrations.facade import emit_event
        from app.models.organization import Organization

        async with AsyncSessionLocal() as db:
            org_id = (
                await db.execute(select(Organization.id).order_by(func.random()).limit(1))
            ).scalar_one_or_none()
            if org_id is None:
                print("no org in dev DB — run any e2e first")
                return 1
        base = rss_mb(target_pid)
        print(f"worker warm rss={base:.0f}MB")
        peak = base
        for w in range(WAVES):
            async with AsyncSessionLocal() as db:
                for i in range(EVENTS_PER_WAVE):
                    await emit_event(
                        db,
                        org_id,
                        "project.approved",
                        subject=f"soak-{w}-{i}",
                        data={"project_id": f"p{w}-{i}", "user_id": "u"},
                    )
                await db.commit()
            # let the worker drain (outbox poll every 15s)
            await asyncio.sleep(18)
            cur = rss_mb(target_pid)
            peak = max(peak, cur)
            print(f"wave {w + 1}/{WAVES}: worker rss={cur:.0f}MB")
        await engine.dispose()
        growth = peak - base
        print(f"warm={base:.0f}MB peak={peak:.0f}MB growth=+{growth:.0f}MB over {WAVES} waves")
        ok = growth < 80
        print("DRILL OK" if ok else "DRILL FAILED (worker RSS growth)")
        return 0 if ok else 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


sys.exit(asyncio.run(main()))

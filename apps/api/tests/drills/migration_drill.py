# ruff: noqa: SIM115, BLE001, S603, S607, E702
"""R355: multi-step migration drill on a scratch DB — zero→head, then
step DOWN 4 revisions one at a time and back UP, verifying each hop."""

import os
import subprocess
import sys
from pathlib import Path

# Repo-relative: this file lives at apps/api/tests/drills/<name>.py
API_DIR = str(Path(__file__).resolve().parents[2])
ROOT = str(Path(__file__).resolve().parents[4])
TMP = str(Path(API_DIR) / ".drill-logs")
Path(TMP).mkdir(exist_ok=True)


PGURL = "postgresql://postgres:postgres@localhost:5432/postgres"
SCRATCH = "intg43_migration_drill"
psql = ["psql", PGURL, "-qAtc"]
subprocess.run(psql + [f'DROP DATABASE IF EXISTS "{SCRATCH}"'], check=True)
subprocess.run(psql + [f'CREATE DATABASE "{SCRATCH}"'], check=True)
env = dict(
    os.environ,
    DATABASE_URL=f"postgresql+asyncpg://postgres:postgres@localhost:5432/{SCRATCH}",
    APP_ENV="test",
)


def alembic(*args):
    return subprocess.run(["uv", "run", "alembic", *args], env=env, capture_output=True, text=True)


def current():
    out = alembic("current")
    return out.stdout.strip().splitlines()[-1] if out.stdout.strip() else "?"


try:
    r = alembic("upgrade", "head")
    if r.returncode:
        print("UPGRADE FAILED")
        print(r.stderr[-800:])
        sys.exit(1)
    print("head:", current())
    hops = []
    for i in range(4):
        d = alembic("downgrade", "-1")
        if d.returncode:
            print(f"DOWN hop {i + 1} FAILED")
            print(d.stderr[-600:])
            sys.exit(1)
        hops.append(current())
        print(f"down {i + 1}:", hops[-1])
    for i in range(4):
        u = alembic("upgrade", "+1")
        if u.returncode:
            print(f"UP hop {i + 1} FAILED")
            print(u.stderr[-600:])
            sys.exit(1)
        print(f"up {i + 1}:", current())
    print("DRILL OK")
finally:
    subprocess.run(psql + [f'DROP DATABASE IF EXISTS "{SCRATCH}"'], check=False)

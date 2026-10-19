# ruff: noqa: S603, S607, BLE001
"""R373: backup/restore drill — prove the database actually restores.

pg_dump (custom format) the live dev DB inside the postgres container,
pg_restore into a scratch database, then assert: the restored
alembic_version matches the source head, and row counts for every intg_*
table (plus users and webhook_subscriptions) match the source exactly.
Scratch DB is dropped afterwards. Backups nobody has restored are
Schrödinger backups.

Run from apps/api with infra up:  uv run python tests/drills/backup_restore_drill.py
"""

import subprocess
import sys
import time

CONTAINER = "openskill-studio-postgres-1"
SRC_DB = "openskill"
SCRATCH = "openskill_restore_drill"
DUMP = "/tmp/openskill_drill.dump"  # inside the container


def sh(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def psql(db: str, query: str) -> str:
    r = sh(["docker", "exec", CONTAINER, "psql", "-U", "postgres", "-d", db, "-tAc", query])
    if r.returncode != 0:
        print(f"psql failed on {db}: {r.stderr[:300]}")
        sys.exit(1)
    return r.stdout.strip()


TABLES_SQL = (
    "SELECT tablename FROM pg_tables WHERE schemaname='public' AND "
    "(tablename LIKE 'intg_%' OR tablename IN ('users','webhook_subscriptions','alembic_version')) "
    "ORDER BY tablename"
)

t0 = time.monotonic()
tables = psql(SRC_DB, TABLES_SQL).splitlines()
src_counts = {t: int(psql(SRC_DB, f"SELECT count(*) FROM {t}")) for t in tables}
src_head = psql(SRC_DB, "SELECT version_num FROM alembic_version")
print(f"source: {len(tables)} tables, head={src_head}, {sum(src_counts.values()):,} rows in scope")

print("dumping (custom format)...")
r = sh(["docker", "exec", CONTAINER, "pg_dump", "-U", "postgres", "-Fc", "-f", DUMP, SRC_DB])
if r.returncode != 0:
    print("pg_dump failed:", r.stderr[:300])
    sys.exit(1)
size = sh(["docker", "exec", CONTAINER, "sh", "-c", f"du -h {DUMP} | cut -f1"]).stdout.strip()
print(f"dump done: {size} in {time.monotonic() - t0:.0f}s")

sh(
    [
        "docker",
        "exec",
        CONTAINER,
        "psql",
        "-U",
        "postgres",
        "-c",
        f"DROP DATABASE IF EXISTS {SCRATCH}",
    ]
)
r = sh(["docker", "exec", CONTAINER, "psql", "-U", "postgres", "-c", f"CREATE DATABASE {SCRATCH}"])
if r.returncode != 0:
    print("createdb failed:", r.stderr[:300])
    sys.exit(1)

print("restoring...")
t1 = time.monotonic()
r = sh(
    [
        "docker",
        "exec",
        CONTAINER,
        "pg_restore",
        "-U",
        "postgres",
        "-d",
        SCRATCH,
        "--no-owner",
        "--exit-on-error",
        DUMP,
    ]
)
if r.returncode != 0:
    print("pg_restore failed:", r.stderr[:400])
    sys.exit(1)
print(f"restore done in {time.monotonic() - t1:.0f}s")

ok = True
restored_head = psql(SCRATCH, "SELECT version_num FROM alembic_version")
if restored_head != src_head:
    ok = False
    print(f"HEAD MISMATCH: src={src_head} restored={restored_head}")
mismatches = []
for t in tables:
    n = int(psql(SCRATCH, f"SELECT count(*) FROM {t}"))
    if n != src_counts[t]:
        mismatches.append((t, src_counts[t], n))
if mismatches:
    ok = False
    for t, a, b in mismatches[:10]:
        print(f"COUNT MISMATCH {t}: src={a} restored={b}")
# spot-check an encrypted webhook secret survived byte-identically (R371)
src_sample = psql(SRC_DB, "SELECT secret FROM webhook_subscriptions ORDER BY id LIMIT 1")
dst_sample = psql(SCRATCH, "SELECT secret FROM webhook_subscriptions ORDER BY id LIMIT 1")
if src_sample != dst_sample:
    ok = False
    print("SECRET BYTES DIFFER after restore")

sh(["docker", "exec", CONTAINER, "psql", "-U", "postgres", "-c", f"DROP DATABASE {SCRATCH}"])
sh(["docker", "exec", CONTAINER, "rm", "-f", DUMP])
print(
    f"head match: {restored_head == src_head}; tables checked: {len(tables)}; "
    f"mismatches: {len(mismatches)}; total {time.monotonic() - t0:.0f}s"
)
print("DRILL", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)

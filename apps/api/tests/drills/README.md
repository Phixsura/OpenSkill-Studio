# Fabric operational drills (ADR-018 §20, window 11)

Each drill is a self-contained foreground script that boots its own
uvicorn, breaks something real, and asserts the documented recovery
semantics. Run from `apps/api` with infra up (`make infra-up`):

| Drill | Breaks | Asserts |
|---|---|---|
| `redis_drill.py` | stops the redis container mid-traffic | fail-open: zero 5xx during outage, full function on restart |
| `minio_drill.py` | stops MinIO, runs an export | run lands as a CLEAN terminal `failed`; rerun after recovery succeeds |
| `crash_drill.py` | kill -9 mid write-storm | no stuck committing/validating jobs, no fresh orphan runs, clean restart |
| `migration_drill.py` | alembic downgrade 4 hops, upgrade back | every hop reversible, head restored |
| `backup_restore_drill.py` | pg_dump -Fc the live DB, pg_restore into a scratch DB | alembic head + every intg_*/users/webhook row count matches; encrypted secrets byte-identical; scratch dropped (R373) |
| `ratelimit_drill.py` | bursts a 10/60 route in dev mode | exactly 10 allowed (X-RateLimit-* present), 11th = 429 with Retry-After, per-route bucket (R366) |

Logs land in `apps/api/.drill-logs/` (gitignored).

    cd apps/api && uv run python tests/drills/redis_drill.py

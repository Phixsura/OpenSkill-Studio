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
| `slow_sink_drill.py` | webhook sink accepts then stalls 60s (slowloris) | EgressClient read-timeout fires at 15s as a clean failure result (no hang/500); fast sink succeeds right after (R380) |
| `explain_audit.py` | nothing — reads query plans on the big dev DB | every fabric hot-path predicate index-scans; any Seq Scan over a >10k-row table is flagged (R387) |
| `soak_drill.py` | N consecutive storms on one process, RSS sampled per storm | no unbounded growth (final < 2x warm, < 1.5 GB); measured: flat 244→230 MB over 12 storms (R398) |
| `ratelimit_drill.py` | bursts a 10/60 route in dev mode | exactly 10 allowed (X-RateLimit-* present), 11th = 429 with Retry-After, per-route bucket (R366) |

Logs land in `apps/api/.drill-logs/` (gitignored).

    cd apps/api && uv run python tests/drills/redis_drill.py

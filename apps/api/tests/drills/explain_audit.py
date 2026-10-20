# ruff: noqa: S603, S607, E501
"""R387 (from the R336 audit): EXPLAIN every fabric hot-path predicate on
the big dev DB and flag any Seq Scan over a table with >10k rows — the
query-plan regression drill. Run from apps/api with infra up:

    uv run python tests/drills/explain_audit.py

Checked in after living as throwaway job tooling (R367 lesson); keep the
QUERIES map in sync with new hot predicates.
"""

import subprocess

DSN = "postgresql://postgres:postgres@localhost:5432/openskill"

QUERIES = {
    "deliveries by sub+status": "SELECT * FROM intg_event_deliveries WHERE subscription_id='x' AND status='pending'",
    "deliveries retention": "SELECT id FROM intg_event_deliveries WHERE status IN ('succeeded','exhausted') AND created_at < now() - interval '90 days' LIMIT 100",
    "events by org+time": "SELECT * FROM intg_events WHERE org_id='x' ORDER BY time DESC LIMIT 50",
    "events export cursor": "SELECT * FROM intg_events WHERE org_id='x' AND id > 'y' ORDER BY time, id LIMIT 500",
    "events retention": "SELECT id FROM intg_events WHERE time < now() - interval '180 days' LIMIT 100",
    "staged by conn+model+ext": "SELECT * FROM intg_staged_records WHERE connection_id='x' AND model='roster.class' AND external_id='y'",
    "staged actives": "SELECT * FROM intg_staged_records WHERE connection_id='x' AND model='roster.class' AND status='active'",
    "runs by profile live": "SELECT id FROM intg_sync_runs WHERE profile_id='x' AND status IN ('queued','running')",
    "runs retention": "SELECT id FROM intg_sync_runs WHERE status IN ('succeeded','failed','cancelled') AND created_at < now() - interval '180 days' LIMIT 100",
    "queue pending by org": "SELECT * FROM intg_identity_match_queue WHERE org_id='x' AND status='pending'",
    "login state expiry purge": "SELECT id FROM intg_sso_login_states WHERE expires_at < now() LIMIT 100",
    "links by conn+subject": "SELECT * FROM intg_identity_links WHERE connection_ref='x' AND subject='s' AND revoked_at IS NULL",
    "links by org+user": "SELECT * FROM intg_identity_links WHERE org_id='x' AND user_id='u' AND source='scim' AND revoked_at IS NULL",
    "members by org+user": "SELECT * FROM org_members WHERE org_id='x' AND user_id='u'",
    "members breakglass": "SELECT id FROM org_members WHERE org_id='x' AND is_break_glass AND status='ACTIVE'",
    "users by lower email": "SELECT * FROM users WHERE lower(email)='a@b.c'",
    "refresh tokens by user": "SELECT * FROM refresh_tokens WHERE user_id='u' AND revoked_at IS NULL",
    "import jobs by org": "SELECT * FROM intg_import_jobs WHERE org_id='x' ORDER BY created_at DESC LIMIT 20",
    "row errors by job": "SELECT * FROM intg_import_row_errors WHERE job_id='x' ORDER BY row_number",
    "export runs by stream": "SELECT * FROM intg_export_runs WHERE stream_id='x' ORDER BY created_at DESC LIMIT 20",
    "subs by org": "SELECT * FROM webhook_subscriptions WHERE org_id='x'",
    "scim groups by org+display": "SELECT * FROM intg_scim_groups WHERE org_id='x' AND lower(display_name)='g'",
    "connections sweep slice": "SELECT * FROM intg_connections WHERE status IN ('active','degraded') ORDER BY updated_at LIMIT 100",
    "domains by org+domain": "SELECT * FROM intg_org_domains WHERE org_id='x' AND domain='d'",
    "domains discovery": "SELECT org_id FROM intg_org_domains WHERE domain='d' AND status='verified'",
    # R545: window-34+ additions
    "sync hook secret lookup": "SELECT * FROM intg_sync_profiles WHERE id='x' AND trigger_secret_hash='h'",
    "deliveries keyset page": "SELECT * FROM intg_event_deliveries WHERE id < 'x' ORDER BY id DESC LIMIT 50",
    "events keyset page": "SELECT * FROM intg_events WHERE org_id='x' AND id < 'y' ORDER BY time DESC LIMIT 50",
    "export streams sweep": "SELECT * FROM intg_export_streams WHERE enabled AND schedule IN ('hourly','daily')",
    "sync profiles sweep": "SELECT * FROM intg_sync_profiles WHERE enabled AND schedule IN ('hourly','daily')",
}


def rows(table: str) -> int:
    out = subprocess.run(
        ["psql", DSN, "-qAtc", f"SELECT count(*) FROM {table}"],
        capture_output=True,
        text=True,
    )
    try:
        return int(out.stdout.strip())
    except ValueError:
        return -1


def main() -> None:
    import re

    flagged = 0
    for label, q in QUERIES.items():
        out = subprocess.run(["psql", DSN, "-qAtc", f"EXPLAIN {q}"], capture_output=True, text=True)
        plan = out.stdout
        if out.returncode:
            print(f"ERR  {label}: {out.stderr.strip()[:90]}")
            continue
        m = re.search(r"Seq Scan on (\w+)", plan)
        if m:
            n = rows(m.group(1))
            if n > 10_000:
                flagged += 1
                print(f"FLAG {label}: Seq Scan on {m.group(1)} ({n} rows)")
            else:
                print(f"ok   {label} (seq on small {m.group(1)}={n})")
        else:
            print(f"ok   {label}")
    print(f"\nflagged={flagged}")


main()

# Integration Fabric — Operations Guide (ADR-018, issue #43)

Audience: platform operators and org admins wiring real IdPs/SIS/LMS/ATS.
Companion to `docs/design/018-enterprise-integration-fabric.md` (the why);
this is the how.

## 1. Connecting an IdP (SSO)

### OIDC (Okta, Entra ID, Auth0, Google Workspace)

1. **Verify a domain first** — Integrations → Identity → claim domain, add
   the TXT record (`osks-verify-…`). The pending-domain sweep polls DNS
   every 15 min; or hit Verify manually. SSO discovery and email matching
   only trust verified domains.
2. Create the OIDC connection with the IdP issuer URL + client id/secret.
   The secret is write-only (`has_client_secret` is all you get back).
3. Register our callback at the IdP: `{PUBLIC_BASE_URL}/api/v1/sso/oidc/callback`.
4. Optional: register back-channel logout —
   `{PUBLIC_BASE_URL}/api/v1/sso/oidc/backchannel-logout/{connection_id}`.
5. Flip the connection to `active`, test via `GET /sso/login?email=user@domain`.

### SAML (ADFS, Shibboleth, Okta SAML)

1. Same domain prerequisite.
2. Preferred: set `idp_metadata_url` and hit **refresh-metadata** — entity
   id, Redirect-binding SSO URL and signing certificates are extracted and
   pinned (encryption-only keys ignored). A daily 05:37 sweep re-polls, so
   IdP cert rotation needs no manual step as long as the IdP publishes
   old+new during the overlap.
3. Without a metadata URL: paste the entity id, SSO URL and PEM cert(s)
   manually. The 06:18 sweep emits `integration.sso.cert_expiring` 30 days
   before `not_after` (daily-deduped) — subscribe a webhook to it.
4. Our SP metadata: `GET /api/v1/sso/saml/metadata`.

### Enforced SSO and break-glass

`enforce_sso=true` on the org blocks password login for everyone except
members with `is_break_glass` (max 2; required BEFORE the flag can be set;
each break-glass login emits `org.breakglass.login`).

## 2. SCIM provisioning (Okta / Entra)

- Mint a token under Identity → SCIM. Shown once; base URL is
  `{PUBLIC_BASE_URL}/api/v1/scim/v2`.
- Deactivation (PATCH active=false, PUT active=false, or DELETE) archives
  the membership AND revokes every refresh token immediately. Re-POST of
  the same userName reactivates instead of 409 (Entra retry behavior).
- `group_map` routes IdP groups to cohorts or roles. Roles cap at
  instructor — mapping to admin/owner is rejected (privilege-escalation
  guard). Group sync never demotes an owner/admin.
- `/Bulk` accepts up to 100 ops per request (1MB cap).

## 3. Roster (OneRoster / LTI)

- OneRoster: create a connection (`oneroster` provider: token_url +
  base_url), then a pull SyncProfile per model (`roster.class`,
  `roster.user`, `roster.enrollment`). Schedules (`hourly`/`daily`) are
  driven by the :03/:33 sweep. Then **provision-roster** applies staged
  records to cohorts: conflicts are reported, never guessed — resolve them
  in the identity queue / conflicts list and run another pass.
- LTI 1.3: register the LMS (issuer, client id, endpoints, deployment-id
  allowlist). Tool JWKS: `GET /api/v1/lti/jwks`. After the first launch of
  a resource link, the NRPS **Sync roster** button pre-provisions course
  members; AGS grade return is per-link opt-in (`grade_sync_enabled`).

## 4. Event mesh (webhooks)

- Subscriptions accept exact legacy names, `com.openskill.*.vN` types, or
  `prefix.*` wildcards. Fabric-internal `integration.*` events match on
  exact name only (no feedback loops into failing endpoints).
- Signature: Standard Webhooks — `v1,base64(HMAC-SHA256(secret, id.ts.body))`
  in `webhook-signature`; verify with the shown-once secret.
- Retry ladder: 0s, 5s, 5m, 30m, 2h, 5h, 10h, 10h → `exhausted`
  (dead-letter) + `integration.delivery.exhausted` event. Five days of
  consistent failure auto-disables the endpoint
  (`integration.subscription.auto_disabled`).
- **Rotate secret** keeps the old key co-signing for 7 days; **Rotate now**
  is the leaked-secret path. **Test** sends a sample signed event
  synchronously and reports status/latency.
- The exact signed bytes of every delivery are archived on first dispatch
  (retries and replays resend them byte-for-byte even across deploys);
  inspect via GET /deliveries/{id}/payload.
- Connectors honor 429 Retry-After (capped at 30s) and retry transient
  5xx twice — a rate-limited SIS no longer fails the run outright.
- Failed attempts keep a sanitized 500-char response snippet in the
  attempts view — first stop when a receiver misbehaves.
- Replay: any terminal delivery can be replayed; replays are flagged
  (`replay_of`) and exempt from the one-original-per-(event,subscription)
  uniqueness.

## 3b. One-click LMS onboarding (R87)

POST /integrations/lti/registrations/dynamic with the platform's
openid-configuration URL (+ its one-time registration token): we fetch the
config, refuse plain OIDC servers, register the tool (private_key_jwt,
resource-link + deep-linking messages, AGS/NRPS scopes) and persist the
returned client_id + deployment ids. Moodle: Site admin → Plugins →
External tool → "register a tool" gives you exactly those two values.

## 3c. Single Logout (R88)

Our SP metadata advertises `/api/v1/sso/saml/slo/{connection_id}`
(Redirect binding). IdP-initiated LogoutRequests MUST be signed — unsigned
or rogue-signed requests are refused (logout-CSRF). On success the user's
sessions are revoked, `integration.sso.single_logout` fires, and a
LogoutResponse is redirected to the IdP's SLO URL (captured automatically
from metadata). OIDC orgs get the same via back-channel logout.

## 4a. Imports: kinds, formats and vendor headers (R92/R128-R131)

Three template kinds (`kind` form field): `users` (email, display_name,
role student|instructor), `roster` (email, cohort_slug, role
learner|instructor — enrolls EXISTING active org members; import users
first), and `opportunities` (title, opportunity_type, description,
location_mode, location_text, compensation_display, openings — lands as
DRAFTS only; a human publishes). Files may be CSV or JSON (a top-level
array, or `{"<kind>": [...]}`); the format is sniffed from content, no
extra field needed.

Pass `header_map` (JSON form field) at upload:
`{"email": "E-mail Address", "display_name": "Full Name", "role": "Role"}`.
The map is persisted on the job, so commit re-parses identically; unknown
canonical keys are refused. Re-imports are idempotent: users match by
email, roster by (user, cohort), opportunities by lower(title) — and an
existing member/posting's role/status is never changed by an import.

Admins can fetch a blank starter file at
`GET .../integrations/imports/template?kind=<users|roster|opportunities>&format=<csv|json>`
(header row + one worked example; the UI's "Download template" button does
this). Every upload/commit is audited (`intg.import.created` /
`intg.import.committed`, counts only), and a successful commit emits
`com.openskill.org.import.committed.v1` on the mesh so downstream
SIS/HRIS webhooks can react to bulk provisioning — the payload carries
counts, never the roster.

## 4b. Editing and removing resources (R77-R84)

Every admin resource is full CRUD:

- Webhook subscriptions: PATCH edits url/events or re-enables an
  auto-disabled endpoint WITHOUT rotating the secret; DELETE removes.
- Export streams: PATCH edits allowlist/anonymize/schedule or disables;
  DELETE removes the stream + run history (bucket objects stay).
- Sync dry-run: `POST .../sync-profiles/{id}/preview?limit=N` (pull profiles,
  the UI "Dry-run" button) reads the first few live records from the connector
  and shows how the mapping transforms them — nothing is staged or committed.
  Use it to validate a connection's read + mapping before enabling a schedule.
  (Sync RUNS load the connection's decrypted credentials just like ping — a
  healthy ping now implies a sync will authenticate the same way.)
- Sync profiles: PATCH edits schedule/enabled/field_policy; the mapping
  version stays pinned until `repin_mapping: true` (an explicit act).
  DELETE refuses while a run is live (409 SYNC_PROFILE_BUSY — cancel it).
- Mapping profiles: DELETE refuses while any sync profile pins it
  (409 MAPPING_IN_USE).
- LTI registrations: DELETE cascades deployments/links/states; launches
  from that platform stop validating immediately.

## 5. Sync engine conflicts

Record-level rows carry `conflict_class`:

| class                   | meaning                                           | typical fix                                                                      |
| ----------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------- |
| `duplicate_external_id` | two source rows share an id                       | fix at source, re-run                                                            |
| `clock_unresolvable`    | most_recent tie / missing timestamps              | adjudicate: Accept theirs / Keep ours (stale adjudications are refused with 409) |
| `missing_reference`     | enrollment points at unknown class                | sync classes first or enable auto-create                                         |
| `role_conflict`         | manual role differs from SIS, or unknown SIS role | human decided — report-only by design                                            |
| `consent_missing`       | talent push without ats_share consent             | learner must grant consent                                                       |
| `ambiguous_identity`    | email unverified/foreign/duplicate                | resolve in the identity queue                                                    |

## 5b. Inbound sync-trigger webhook (R497, CDC-lite)

Instead of waiting for the hourly/daily schedule, the SOURCE system can
notify the fabric that its data changed:

1. Sync page → profile row → **Webhook trigger** mints the secret (shown
   once; sha256 at rest; minting again rotates, **Disable hook** turns it
   off — both audited).
2. Configure the source system to
   `POST /api/v1/integrations/sync-hooks/{profile_id}` with
   `Authorization: Bearer sth_…` on change events.
3. The fabric enqueues a normal INCREMENTAL run (`trigger="webhook"`,
   cursor from the last run; a live run is reused, so notification storms
   coalesce). The request body is ignored by design — cursors stay
   destination-confirmed; an untrusted payload cannot steer them.
4. Any mismatch (wrong id, wrong/cleared secret) is a uniform 401 — the
   unauthenticated surface has no existence oracle. Rate limit: 30/60s.

## 6. Scheduled jobs (worker crons)

| job                   | schedule        | does                                                                                                                                                  |
| --------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| intg_domain_sweep     | :07/:22/:37/:52 | DNS-poll pending domains, expire after 7d                                                                                                             |
| intg_scheduled_syncs  | :03/:33         | trigger due hourly/daily sync profiles                                                                                                                |
| intg_stale_run_reaper | :09/:39         | fail runs stuck in running                                                                                                                            |
| intg_conn_health      | :14/:44         | ping active/degraded connections; alert on unhealthy transition                                                                                       |
| intg_retention        | 03:52           | age out terminal deliveries (90d), events/runs/row-errors (180d); purge stored import FILES for terminal jobs >90d (R134 — they are full PII rosters) |
| intg_metadata_refresh | 05:37           | re-poll SAML IdP metadata (cert rotation)                                                                                                             |
| intg_cert_expiry      | 06:18           | 30-day cert expiry alerts                                                                                                                             |
| intg_exports          | :47 hourly      | run due export streams (per-stream cadence: hourly/daily)                                                                                             |

All registered names are pinned by `test_every_fabric_sweep_has_a_registered_cron`.

## 6b. Worker health in production compose (R547)

The worker container reuses the API image, whose HEALTHCHECK curls
:8000/health — a worker serves no HTTP, so it reported permanently
UNHEALTHY. The compose service now checks the key a live arq worker
actually maintains (`arq:queue:health-check` in redis, verified
empirically); the one-shot `migrate` job disables the inherited check.

## 6c. Production compose required secrets (R549/R550)

Start from the checked-in template: `cp .env.prod.example .env.prod`, fill
every empty value, then `docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet`
to fail fast before any container starts (R558).

`docker compose -f docker-compose.prod.yml up` refuses to interpolate
without: DB_PASSWORD, JWT_SECRET, S3_ACCESS_KEY, S3_SECRET_KEY and
CREDENTIAL_ENCRYPTION_KEY (a REAL Fernet key — 32-byte urlsafe base64,
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` —
not a passphrase). The migrate job needs the same set: settings import runs
the production boot validators before alembic does anything.

## 6d. Credential key rotation (R574)

Rotate by PREPENDING the new Fernet key:
`CREDENTIAL_ENCRYPTION_KEY=<new>,<old>` — new writes encrypt under the new
key, old rows keep decrypting. Each stored connection credential records
the key GENERATION (count of configured keys) it was encrypted under in
`key_version`; rows with `key_version` below the current generation are the
re-encrypt worklist — re-saving a credential (same values is fine)
re-encrypts it under the newest key and advances its version. Instead of re-saving by hand, run the sweep (R575):

```bash
docker compose -f docker-compose.prod.yml exec api uv run python -m app.cli reencrypt-credentials
```

It re-encrypts every encrypted-at-rest row (connection credentials incl.
key_version bump, webhook signing secrets current+prev, OIDC client
secrets, LTI tool private keys, workflow org credentials) under the newest
key, prints per-table counts, lists any UNDECRYPTABLE rows (a key that is
no longer configured — those credentials must be re-entered by their
owners) and exits 2 when any exist. Drop the old key from the env only
after a clean run:

```sql
SELECT connection_id, key_version FROM intg_connection_credentials
WHERE key_version < <current generation>;
```

## 7. Health and alerting

`GET /orgs/{org}/integrations/health` (the hub strip polls it): connection
status counts, disabled subscriptions, pending/exhausted deliveries,
identity-queue depth, 24h sync failures, active SSO count.

Alertable mesh events to subscribe to:
`integration.delivery.exhausted`, `integration.subscription.auto_disabled`,
`integration.connection.unhealthy`, `integration.sso.cert_expiring`,
`integration.sso.backchannel_logout`.

### Concurrency guarantees (window 5)

Every admin write that races itself is serialized or savepoint-guarded: org
domain claims (org row lock, exact 20-domain cap), export runs (stream row
lock — a manual trigger racing the hourly sweep can neither double-export
nor regress the cursor), first-time credential sets, and same-idempotency-key
import uploads all absorb concurrent duplicates with a clean idempotent
response instead of a 500. The expensive triggers (`.../run` on export
streams, `.../provision-roster`) are rate-limited 10/min per route.

### Outage semantics (window 11, R362 — drilled live)

Redis down: API keeps answering (metering + rate limiting fail OPEN by
design; an outage is an infra alert, not an API kill). Object storage
down: export runs land as terminal `failed` rows and the NEXT run after
recovery re-exports the same span (cursor advances only on success).
API process kill -9: safe — imports are single-transaction (a crash rolls
back to `previewed`), crashed sync runs are reaped by the stale-run
sweeper, delivery retries resume from the outbox.

### Response hardening (window 11, R355)

Every /api response carries `Cache-Control: no-store` (token-gated JSON
must not be cached by intermediaries or the browser) plus the standard
security headers, and the app overrides `Server`. Deployments should ALSO
start uvicorn with `--no-server-header` (our make targets and E2E runners
do) so the stack is not fingerprinted at the protocol layer.

### CI coverage (window 10, R322–R324)

Every PR now runs, besides the full backend suite: the fabric Playwright
sweep (`apps/web/e2e/sweep-integrations.spec.ts` — the five admin pages,
one real create per page, shown-once secret semantics) inside the
Playwright job, and a dedicated `e2e-integration-fabric` job that boots
postgres/redis/MinIO, migrates to head and runs the 62-check live-HTTP
lifecycle (`make e2e-intg`). Fabric source files are ruff-format clean
(the CI lint job enforces `ruff format --check`).

### Browser E2E

> Flake rule (R363): never use `waitUntil: "networkidle"` against the
> next-dev server — HMR holds a connection open and each navigation
> stalls ~30 s. Use `"load"` plus a short settle sleep, and pre-warm
> dev compiles before the walk.
> (window 9, R281–R285)

`apps/api/tests/browser_e2e_integrations.mjs` walks the whole fabric admin
journey in a real Chromium: register → org → hub (catalog, health strip,
New-connection form) → identity (domain claim with TXT token, freemail
rejection UX, SCIM token mint with shown-once secret) → events (datalist
catalog, subscription create with shown-once signing secret, bad-URL
rejection UX) → sync → data (export-stream create, template download, full
CSV import upload→preview→commit→member-visible) → mobile-viewport sweep
(390px, no page-level x-overflow) — with a console gate that fails on any
JS exception or React warning. Run: web on :3000, api on :8000
(APP_ENV=test), `node tests/browser_e2e_integrations.mjs`.

### Per-org resource caps (window 8, R260–R263)

All count-then-insert caps are serialized under a `FOR UPDATE` org-row lock
(the R208/R113 idiom), so they hold under concurrent admin writes:

| Resource                      | Cap                        | Error code                       |
| ----------------------------- | -------------------------- | -------------------------------- |
| Break-glass designees         | 2                          | `BREAK_GLASS_LIMIT`              |
| SCIM tokens (active)          | 5                          | `SCIM_TOKEN_LIMIT`               |
| SSO connections               | 5                          | `SSO_LIMIT_REACHED`              |
| Integration connections       | 20                         | `CONNECTION_LIMIT_REACHED`       |
| Export streams                | 20                         | `EXPORT_LIMIT_REACHED`           |
| Sync profiles                 | 50                         | `SYNC_PROFILE_LIMIT_REACHED`     |
| LTI registrations             | 10                         | `LTI_REGISTRATION_LIMIT_REACHED` |
| deployment_ids per LTI create | 50                         | `LTI_REGISTRATION_INVALID`       |
| Org domains                   | 20                         | `DOMAIN_LIMIT_REACHED`           |
| Webhook subscriptions         | per `MAX_WEBHOOKS_PER_ORG` | `WEBHOOK_LIMIT_REACHED`          |

The connection/stream/profile caps exist because the shared sweeps
(half-hourly pings, hourly exports, scheduled syncs) fan out over those
rows for every org — one tenant must not degrade every tenant's scheduler.

Whole-class SIS removals now unenroll members: the tombstone pass resolves
cohorts through the connection backlink map, so offboarding a class in the
SIS removes its memberships on the next provision pass.

### Scale & protocol guarantees (window 6)

- A connector page of ANY size is staged completely; the cursor only advances
  after the whole page commits (crash replays are idempotent upserts).
- Offset pagination is bounded (10k pages/read) — a server that ignores
  `offset` fails the run cleanly instead of looping forever.
- Egress responses stream and abort at the 1MB cap — an oversized body can
  no longer buffer unbounded memory before the cap fires.
- The N+1 sweep batched every per-record lookup: pull engine, push, roster
  provisioning, SCIM directory listing, and both import previews now issue
  bounded IN(500) queries instead of a round-trip per row.
- A webhook endpoint answering 410 Gone is disabled immediately (Svix
  convention) and alerts via `integration.subscription.auto_disabled`
  (reason `endpoint_gone`).
- Fixing an errored connection's config or base_url re-opens it for a fresh
  ping, same as rotating credentials.
- Every slow-IO sweep is kill-durable: health pings run a bounded
  stalest-first slice per tick and commit per connection; the SAML metadata
  refresh and the domain-DNS sweep commit per row; all three crons carry
  explicit 1800s timeouts. A mid-sweep kill never rolls back completed work.

### Guard rails & verification (window 7)

- Drift guards fail CI when hand-maintained registries fall out of sync:
  every emitted mesh-event name must appear in the subscription catalog
  (source-scan test), every canonical model declares strict-schema keys, and
  every non-manual schedule has a sweep cadence (plus the import-kind triple).
- Clean-harness mutation re-verification: 39 mutants killed across the
  security cores this window (projection, signing, deprovision, SAML
  window/XSW/cert-pinning, retry-ladder boundaries, identity takeover
  ladder, LTI launch, OIDC state/PKCE, import fingerprint, outbox worker,
  roster governance, push consent, export data-key gate); the two survivors
  are documented equivalents with outcome-level tests pinning the property.
- Mutation harness hygiene: probes clear **pycache** after writing AND after
  restoring a mutant — a restored source can otherwise keep executing the
  mutant's bytecode (mtime-granularity collision).

### Mix-up defenses (window 8)

Issuer/entity binding is enforced at every trust-bootstrap point: OIDC
discovery metadata must carry the configured issuer (RFC 8414 §3.3), a SAML
metadata refresh refuses a document whose entityID differs from the
configured IdP entity (nothing is adopted from it), and LTI dynamic
registration refuses a configuration whose issuer lives on a different
origin than the admin-pasted URL. Conflict adjudication now also verifies
the result row belongs to the addressed run (uniform 404 otherwise).

## 7a1b. Live-suite meta-target (R567)

`make e2e-intg-all` runs every fabric live-HTTP suite (lifecycle, scale,
fuzz x2, SCIM conformance, latency, storm, races, adversarial) strictly
sequentially. They share the dev database — running any two of them, or any
of them against the pytest battery, concurrently produces phantom failures.
The meta-target encodes that rule; use it instead of ad-hoc parallel runs.

## 7a2. Drills (`make drills`, R399)

`make drills` (infra up, ~10 min) runs every operational drill in
`apps/api/tests/drills/` sequentially and fails fast — outage semantics,
crash recovery, migration reversibility, limiter engagement, slow-sink
timeout, backup/restore, query plans, RSS soak. Run it before a release
cut or after infra-level changes.

## 7b. Audit trail (window 12, R377/R384)

Every mutating `/integrations` route writes `cp_audit_events` via
`record_fabric_audit` (actor, target, config-shape payload — never
secrets) or sits on an explicit exempt list (pings, previews, LTI
protocol surfaces). Three composed guards keep this honest: action
literals must be registered in `AUDIT_ACTIONS` (unregistered = silent
no-op), every mutating route must call-or-declare (structural test), and
a DB test proves a row actually lands. Break-glass (`intg.break_glass.set`)
is the headline entry an auditor will ask for.

R592–R597 completed the chain end to end:

- **IdP-driven events are audited too** — SCIM provision/reactivate/
  deprovision/group-delete and SSO JIT provisioning record a `system`-actor
  row (no human performed them); the NRPS bulk pull records the operation
  under the admin who ran it. Guard: any fabric `OrgMember(` construction
  without an audit trail fails `test_access_grant_audit_guard_db.py`.
- **Tenant-visible** — all 46 `intg.*` actions are in
  `TENANT_VISIBLE_ACTIONS`, so the org's own audit feed
  (`GET /tenants/{id}/audit-events`, owner/billing_admin) shows the full
  integration history; a guard fails if a new fabric action is omitted.
- **Retention & export posture** — `cp_audit_events` is append-only and is
  deliberately NEVER swept by the retention cron (compliance records
  outlive operational data; a purge horizon is a business/legal decision,
  not an engineering default). The feed query is served by
  `(tenant_id, created_at)`, so growth does not degrade it. Export = page
  the feed API (`page`/`per_page≤200`, optional `action` filter) into the
  external compliance store; payloads are config-shape only, never secrets.

## 7c. Admin list pagination (R375/R376)

`GET .../events` and `.../deliveries` take `before=<last id>` (keyset —
ULIDs are time-ordered; stable under concurrent inserts) and return
`meta: {next_cursor, has_more}`. The events page exposes it as
"Load older".

## 7d. Accessibility gate (R372/R383)

`make e2e-intg-a11y` (local) and `sweep-a11y-integrations.spec.ts` (CI
Playwright job) run axe-core WCAG 2.1 A/AA over the five fabric pages as
an authenticated admin; any serious/critical violation fails.

## 7e. Production startup ordering (R552)

`docker compose -f docker-compose.prod.yml up` enforces:
`postgres/redis/minio healthy` → `migrate` exits 0 (`alembic upgrade head`,
idempotent — it re-runs on every up) → `api`/`worker` start → `api` reports
healthy (image HEALTHCHECK on `GET /api/v1/health`) → `web` starts. Do not
weaken the `service_completed_successfully` / `service_healthy` conditions
to the bare list form: that only orders container creation, and on a first
deploy the API will serve against an empty database.

## 7f. Backups (R564)

The prod compose persists three volumes: `pgdata` (system of record),
`miniodata` (uploaded artifacts/export parts), `redisdata` (billing
counters, AOF). Nothing backs them up automatically — schedule this on the
host (cron/systemd timer):

```bash
# Postgres — custom-format dump, restorable table-by-table (verified R564)
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc -Z6 > "backup-$(date +%F).dump"

# Restore (into a fresh database; stop api/worker first)
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists < backup-YYYY-MM-DD.dump

# MinIO — mirror the bucket out of the container
docker compose -f docker-compose.prod.yml exec -T minio \
  sh -c 'mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" && mc mirror local/openskill /backup'
```

Redis is derived + billing-counter state: the AOF in `redisdata` survives
restarts; for disaster recovery a lost hour of API-usage counters is the
accepted exposure (metering fails open by design, R92[H2]). Test the
restore path with `make drills` (backup_restore_drill) before relying on it.

## 8a. Production web serving topology (R528 — read before deploying)

The web app is `output: standalone`. Three rules the hard way:

1. **Serve with `node .next/standalone/apps/web/server.js`** (after copying
   `.next/static` → `.next/standalone/apps/web/.next/` and `public/`).
   `next start` is UNSUPPORTED on standalone builds — it boots but silently
   drops rewrite-proxy responses.
2. **Same-origin API via the rewrite proxy.** CSP is `connect-src 'self'`,
   so the browser must call relative `/api/v1/*`. Set `API_PROXY_URL`
   (server-only, read at BUILD time by the rewrite) to the API origin —
   never bake `NEXT_PUBLIC_API_URL`, which both violates CSP and inlines
   the origin into the bundle. Prefer an explicit IP/hostname the Node
   process can dial (`localhost` can resolve ::1 while uvicorn binds v4).
3. **Monorepo checkouts need `outputFileTracingRoot`** (pinned in
   next.config) — without it a worktree/second-lockfile checkout produces
   an EMPTY standalone directory and there is no server.js at all.

## 8. Security posture (what to tell the auditor)

Single-egress SSRF discipline (resolve → validate every IP → dial pinned
literal with Host/SNI; mixed public+private resolution refused; enforced by
a lint test), write-only Fernet credential envelopes (webhook signing secrets
included since intg19 — rotate via CREDENTIAL_ENCRYPTION_KEY MultiFernet), uniform-404 IDOR
walls, per-route rate limits on every unauthenticated protocol surface
(guard test), XSW-safe SAML (only the signed subtree is consumed; exclusive
c14n), nonce/state single-use with replay caches, SCIM deprovision sweeps
sessions, export allowlist-built projections with org-salted hashing, and
~200 hand-rolled mutation-probe killers across all nine fabric cores.

Window-35 additions (R512/R513): binding an EXISTING platform account via
SCIM or bulk import requires a VERIFIED claim on the email's domain — the
same rule SSO identity resolution always applied — so no tenant can
conscript, deprovision-sweep, or rename a foreign account; and SAML SLO
refuses duplicate signed query parameters, parses exactly the signed
segment, and enforces an IssueInstant freshness window with single-use
request IDs (a captured logout redirect is not a replayable
session-revocation weapon).

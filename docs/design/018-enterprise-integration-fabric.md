# ADR-018: Enterprise Integration Fabric

Issue #43. Research basis: `research-issue-43-world-class.md` (streams S1–S8,
recommendations R1–R8). Status: accepted, implementation phased (§17).

## 1. Problem

Schools, enterprises and partners already run identity (Okta/Entra), SIS/LMS
(PowerSchool/Canvas), HRIS/ATS (Workday/Greenhouse), CRM (Salesforce/HubSpot) and
warehouses. OpenSkill Studio must become a system of engagement inside those stacks —
without one-off connector code, credential leakage, cross-tenant identity bridges, or
sync jobs that silently half-write. This ADR defines a governed integration fabric:
connection model, enterprise SSO/SCIM, canonical roster/talent/CRM sync, an event mesh,
a bounded mapping language, bulk import/export, and a connector SDK boundary.

## 2. Safety posture (non-negotiable, mirrors ADR-016 §1 / ADR-017 §2)

1. **Credentials are write-only.** Stored via `core/crypto.py` envelope encryption;
   API responses never echo secrets (R79/R82 `_card_fields`-style total coverage:
   every response model field is explicitly allowlisted).
2. **No tenant code execution.** Mapping is declarative data (§10); connector behavior
   ships in-repo behind declared capabilities (§13). Same invariant as R83
   (no code in manifests).
3. **One egress path.** All outbound HTTP (webhook delivery, connector calls, IdP
   metadata fetch) goes through `integrations/security.py::EgressClient` (§14.1).
   Direct httpx use in `app/integrations/` outside that module fails review + a lint
   test asserts it.
4. **External systems never hard-delete platform data.** Inbound deletes become
   tombstone events + soft deactivation; cascades require explicit admin confirmation.
5. **Identity links are tenant-scoped and reversible.** Linking, never merging, by
   default; ambiguous matches queue for admin confirmation (§9).
6. **403-vs-404 uniformity** (R88 class 2): cross-tenant reads AND writes of
   connections, sync runs, import jobs, deliveries return 404, never 403.

## 3. Package layout (copies the mature `ecosystem/` shape)

```
app/integrations/
  __init__.py
  facade.py            # the ONLY surface other packages may import
  security.py          # EgressClient (SSRF-safe), webhook signing, SCIM auth
  worker.py            # arq worker: delivery dispatch, sync runs, cert-expiry cron
  models/
    __init__.py        # re-exports; tables prefixed intg_
    provider.py        # IntegrationProvider (catalog), ConnectorCapability
    connection.py      # IntegrationConnection, ConnectionCredential
    sso.py             # SsoConnection, OrgDomain, ScimToken
    identity.py        # ExternalIdentityLink, IdentityMatchQueue
    roster.py          # canonical RosterTerm/RosterClass/RosterEnrollment staging
    lti.py             # LtiRegistration, LtiDeployment, LtiLaunchNonce, LtiLineItemMap
    sync.py            # SyncProfile, MappingProfile, SyncRun, SyncRecordResult
    events.py          # IntegrationEvent (CloudEvents log), EventDelivery(+Attempt)
    bulk.py            # ImportJob, ImportRowError
    export.py          # ExportStream, ExportRun
  schemas/             # pydantic (extra="forbid" on all inbound — R85)
  services/
    connections.py     # CRUD + credential lifecycle + health
    sso_saml.py        # SAML SP (python3-saml behind interface)
    sso_oidc.py        # OIDC RP (authlib)
    domains.py         # DNS TXT verification
    scim.py            # SCIM 2.0 server logic (scim2-models payloads)
    identity.py        # resolution algorithm §9
    roster.py          # canonical roster ingest → Cohort/Org provisioning
    lti.py             # launch validation, deep linking, AGS push
    mapping.py         # mapping document validation + evaluation + preview
    sync_engine.py     # run orchestration, cursors, checkpoints, conflicts
    events.py          # emit (outbox), deliver, replay, DLQ
    bulk_import.py     # dry-run/commit pipeline
    warehouse.py       # governed export streams
  api/                 # routers; mounted under /api/v1
```

DB tables all prefixed `intg_` (as `cp_` for controlplane). Worker reuses the
controlplane outbox pattern: handlers registered via decorator, idempotent,
`process_outbox_once(db)` drivable inline in tests.

## 4. Part A — Connection model

### 4.1 `intg_providers` (code-seeded catalog; Nango `providers.yaml` analog)

| column                  | type                 | notes                                                                                                                           |
| ----------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| id                      | VARCHAR(26) PK       | ULID                                                                                                                            |
| key                     | VARCHAR(100) UNIQUE  | e.g. `oneroster`, `clever`, `generic_webhook`, `scim_idp`, `saml_idp`, `oidc_idp`, `lti_platform`, `csv_import`, `warehouse_s3` |
| category                | VARCHAR(30)          | enum: `identity, roster, lms, hris, ats, crm, storage, messaging, erp, warehouse, generic`                                      |
| auth_mode               | VARCHAR(30)          | enum: `oauth2_cc, oauth2_ac, api_key, basic, saml_metadata, oidc_discovery, none`                                               |
| display_name            | VARCHAR(200)         |                                                                                                                                 |
| capabilities            | JSONB                | list of capability keys (§13), e.g. `["roster.read", "gradebook.write"]`                                                        |
| config_schema           | JSONB                | JSON Schema for per-connection config (drives setup UI)                                                                         |
| version                 | INTEGER              | incrementing; connections pin it (Prismatic rule: no auto-upgrade)                                                              |
| enabled                 | BOOLEAN default true | kill switch                                                                                                                     |
| created_at / updated_at | timestamptz          |                                                                                                                                 |

Seeded by migration + `services/connections.py::sync_provider_catalog()` from an
in-repo registry dict (same pattern as capability seeding in ADR-011). Rows are never
deleted; disabling sets `enabled=false`.

### 4.2 `intg_connections`

| column                  | type                       | notes                                                                                                    |
| ----------------------- | -------------------------- | -------------------------------------------------------------------------------------------------------- |
| id                      | PK ULID                    |                                                                                                          |
| org_id                  | FK organizations CASCADE   | tenant scope — **every** fabric row hangs off a connection or org                                        |
| provider_id             | FK intg_providers RESTRICT |                                                                                                          |
| provider_version        | INTEGER                    | pinned at creation; explicit upgrade endpoint                                                            |
| name                    | VARCHAR(200)               | admin label                                                                                              |
| status                  | VARCHAR(20)                | enum `pending, active, degraded, disabled, error`                                                        |
| config                  | JSONB                      | validated against provider.config_schema (extra keys rejected)                                           |
| base_url                | VARCHAR(500) NULL          | provider instance URL (e.g. district OneRoster root); egress-validated at write AND at every use (§14.1) |
| health                  | JSONB                      | `{last_ok_at, last_error_at, last_error_class, consecutive_failures}`                                    |
| created_by              | FK users SET NULL          |                                                                                                          |
| created_at / updated_at |                            |                                                                                                          |

Indexes: `ix_intg_conn_org (org_id, status)`, `uq_intg_conn_org_name (org_id, name)
UNIQUE`.

State machine: `pending → active` (credential verified via a provider ping) ·
`active ↔ degraded` (consecutive_failures ≥ 3 sets degraded; success resets) ·
`* → disabled` (admin) · `* → error` (auth permanently rejected — 401/invalid_grant
twice in a row). Only `active|degraded` connections are scheduled.

### 4.3 `intg_connection_credentials` (write-only)

| column        | type               | notes                                                        |
| ------------- | ------------------ | ------------------------------------------------------------ |
| id            | PK ULID            |                                                              |
| connection_id | FK CASCADE, UNIQUE | 1:1 — rotation replaces in place                             |
| kind          | VARCHAR(30)        | `oauth2_tokens, api_key, basic, client_secret`               |
| ciphertext    | TEXT               | `core/crypto.py` envelope (JSON blob inside: tokens, expiry) |
| key_version   | INTEGER            | for crypto key rotation                                      |
| expires_at    | timestamptz NULL   | access-token expiry (plaintext copy for scheduling)          |
| rotated_at    | timestamptz        |                                                              |

Rules (from Nango, S4.2): refresh under a **per-connection advisory lock**
(`pg_advisory_xact_lock(hashtext(connection_id))`) so concurrent runs never race a
refresh. _Implementation note (R314 audit)_: the shipped connectors hold NO
stored OAuth refresh tokens — OneRoster mints a fresh `client_credentials`
token per run and CRM/ATS use static api_keys — so there is no refresh flow
to lock; the invariant the lock was for is held by construction (plus the
one-live-run partial unique index and the queued→running claim). Revisit if
a connector with genuine refresh-token rotation lands.
Rotated refresh tokens would overwrite previous ciphertext in the same txn; a
refresh failure with `invalid_grant` moves the connection to `error` and emits
`integration.connection.unhealthy`. API never returns credential material — the
credential response model has exactly `{id, kind, expires_at, rotated_at}`.

Error codes (this part): `PROVIDER_NOT_FOUND`, `PROVIDER_DISABLED`,
`CONNECTION_NOT_FOUND` (also for cross-tenant), `CONNECTION_CONFIG_INVALID` (422,
schema violations listed per-field), `CONNECTION_NAME_TAKEN`, `EGRESS_BLOCKED` (422 —
base_url resolves to a private range).

## 5. Part B — Enterprise identity

### 5.1 `intg_org_domains` (WorkOS model, S1.1)

| column             | type             | notes                                                                     |
| ------------------ | ---------------- | ------------------------------------------------------------------------- |
| id                 | PK ULID          |                                                                           |
| org_id             | FK CASCADE       |                                                                           |
| domain             | VARCHAR(255)     | lowercased, punycode-normalized at write                                  |
| status             | VARCHAR(20)      | `pending, verified, failed`                                               |
| verification_token | VARCHAR(64)      | `osks-verify-{32 hex}` — value of the DNS TXT record                      |
| verified_at        | timestamptz NULL |                                                                           |
| last_checked_at    | timestamptz NULL | worker cron polls pending domains (15 min cadence, 7-day expiry → failed) |

Index: `uq_intg_domain_verified UNIQUE (domain) WHERE status='verified'` — **partial
unique**: one verified holder per domain globally; many orgs may have the same domain
pending. Claiming a domain another org verified → 409 `DOMAIN_ALREADY_VERIFIED`.
Reserved namespaces (R88: org-settings rule) apply: public-mailbox domains
(gmail.com, outlook.com, qq.com, 163.com, …, in-repo denylist) are rejected at create
with `DOMAIN_NOT_ELIGIBLE` — JIT routing off a freemail domain is a takeover vector.

### 5.2 `intg_sso_connections`

| column                       | type                          | notes                                                                                                                      |
| ---------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| id                           | PK ULID                       |                                                                                                                            |
| org_id                       | FK CASCADE                    |                                                                                                                            |
| protocol                     | VARCHAR(10)                   | `saml` \| `oidc`                                                                                                           |
| status                       | VARCHAR(20)                   | `draft, testing, active, disabled`                                                                                         |
| idp_entity_id                | VARCHAR(500) NULL             | SAML                                                                                                                       |
| idp_metadata_url             | VARCHAR(500) NULL             | polled every 24h for cert pre-publication (S1.2 §5)                                                                        |
| idp_certificates             | JSONB                         | list of `{fingerprint_sha256, pem, not_after, source}` — **multiple concurrent certs accepted; pinned to THIS connection** |
| idp_sso_url                  | VARCHAR(500) NULL             |                                                                                                                            |
| oidc_issuer / oidc_client_id | VARCHAR(500/255) NULL         | OIDC; client_secret lives in a ConnectionCredential-style ciphertext column `oidc_client_secret_ct`                        |
| attribute_map                | JSONB                         | `{email: "...", given_name: "...", external_id: "..."}` — IdP attribute names                                              |
| enforce_sso                  | BOOLEAN default false         | org members with a matching verified-domain email MUST use SSO                                                             |
| allow_jit                    | BOOLEAN default false         | JIT provision on first login (verified domain only)                                                                        |
| default_role                 | VARCHAR(30) default 'student' | JIT role — **never above instructor** (R88 role-mint: `<=` gate; owner/admin cannot be JIT-minted)                         |
| created_at / updated_at      |                               |                                                                                                                            |

Index: `ix_intg_sso_org (org_id, status)`.

SP side is fixed per environment: SP Entity ID
`https://{host}/api/v1/sso/saml/metadata`, ACS `.../api/v1/sso/saml/acs/{sso_connection_id}`
(connection id in the path → assertions are validated **only** against that
connection's pinned certs — the cross-tenant forgery test asserts an assertion signed
by tenant A's cert against tenant B's ACS 401s).

SAML validation sequence (every ACS post; each failure = 401
`SSO_ASSERTION_INVALID` with a `reason` detail logged, not returned):
schema-validate → canonicalize → verify signature on response AND assertion against
pinned certs (reference URI exact; SHA-256+ only) → audience == SP entity id →
`NotBefore/NotOnOrAfter` with 90s skew → `InResponseTo` matches an outstanding
request id (single-use, 10-min TTL, Redis) → assertion ID unseen (replay cache keyed
`saml:aid:{id}` with TTL = NotOnOrAfter) → RelayState ∈ allowlisted return paths.
OIDC path: authlib code flow with `state`+`nonce` (single-use), issuer/aud checks,
JWKS cached with kid-miss single refetch rate-limited 30s (same rule as LTI §8).

Both protocols normalize to one struct:
`VerifiedExternalIdentity {sso_connection_id, subject, email, email_verified, attrs}`
→ identity resolution §9.

Enforced SSO + break-glass: when `enforce_sso=true`, password/refresh login for users
whose email domain matches a verified org domain fails 403 `SSO_REQUIRED` — **except**
users holding `is_break_glass=true` on their OrgMember row (new column, settable only
by an owner, max 2 per org, cannot be the JIT default, WebAuthn-or-TOTP required).
Every break-glass login writes an `intg_events` audit row `org.breakglass.login`
with IP + UA. Cert rotation runbook requirement (S1.3): the rotation endpoint refuses
(`409 BREAK_GLASS_UNVERIFIED`) if no break-glass login succeeded in the last 90 days
and enforce_sso is on — forcing the escape hatch to stay tested.

Login audit: every SSO login (success/failure+reason) appends to `intg_events`
(`org.sso.login` / `org.sso.login_failed`) — queryable via the admin API §15.

### 5.3 SCIM 2.0 server (`/api/v1/scim/v2/...`)

Auth: `intg_scim_tokens` — per-org bearer tokens, `token_hash` (SHA-256), prefix
`osks_scim_`, `last_used_at`, revocable, max 5 active per org. SCIM requests resolve
the org from the token — the URL carries no org id (IdPs can't be asked to template
paths). 401 on unknown/revoked token; 429 + `Retry-After` via the shared rate-limit
middleware (bucket per token).

Endpoints (RFC 7644; payloads via `scim2-models`): `/ServiceProviderConfig`,
`/ResourceTypes`, `/Schemas`, `/Users` + `/Users/{id}`, `/Groups` + `/Groups/{id}`
(GET/POST/PUT/PATCH/DELETE; no `/Bulk` in v1 — advertised as unsupported in
ServiceProviderConfig).

Behavior rules (S2.2 — each is a test):

1. `active:false` via PATCH **or** PUT ≡ DELETE: OrgMember → `archived`, user's
   refresh tokens for this org's sessions revoked immediately (reuses the R88 revoke
   sweep incl. rotation predecessors), SCIM resource kept with `active:false`.
   DELETE does the same and returns 204. Record retained ≥90 days.
2. Lenient PATCH parse: op case-insensitive; `value` may be boolean, `"false"`,
   `"False"`, or `{"active": false}`; paths accept fully-qualified URNs.
   Invalid op ⇒ whole request 400 scimType `invalidSyntax` — no partial apply.
3. Group PATCH applies **member deltas** in one transaction; `remove` supports
   filtered path `members[value eq "{id}"]`. Groups map to cohort membership or org
   roles via a per-connection `group_map` JSONB on the SCIM token row
   (`{"IdP Group Name": {"kind": "cohort", "id": "..."} | {"kind":"role","role":"instructor"}}`,
   admin-managed; unmapped groups are stored but have no effect).
4. Duplicate POST (`userName` exists in org scope) ⇒ 409 scimType `uniqueness`.
   POST reusing a soft-deleted userName **reactivates** (no 409) — draft-ansari rule.
5. `GET /Users?filter=userName eq "x"` supported (plus `externalId eq`); other
   filters 501 scimType `tooMany`... v1 scope: eq on userName/externalId/email only
   (via scim2-filter-parser with a 3-attribute map). ListResponse envelope always.
6. `externalId` stored on the identity link (§9) — updates/deletes resolve by id or
   externalId.
7. SCIM errors are SCIM-shaped (`urn:ietf:params:scim:api:messages:2.0:Error`), not
   the app envelope; bodies never include stack traces or payload echoes. Audit rows
   record op/requestor-token-id/status/resource-id, never attribute payloads (PII).

Provisioned users: created with `status=pending_claim` user rows (no password; email
verification not required when the org domain is verified), org membership `student`
unless group-mapped. SCIM never touches users outside the token's org (cross-org id
⇒ 404-shaped SCIM error).

## 6. Part C — Education integrations (canonical roster)

Canonical staging tables mirror OneRoster 1.2 entities so the OneRoster/Clever/CSV
connectors are mappings, not schema changes. Staging is per-connection and append-
reconciled; **provisioning into Cohort/OrgMember is a separate explicit step** with
conflict reporting — external data never writes production tables directly.

### 6.1 `intg_roster_terms` / `intg_roster_classes` / `intg_roster_enrollments`

Common columns on all three: `id` PK, `connection_id` FK CASCADE, `external_id`
VARCHAR(255) (provider's sourcedId), `payload` JSONB (mapped canonical fields),
`raw_hash` CHAR(64) (SHA-256 of mapped payload — change detection), `status`
(`active, tombstoned`), `first_seen_run_id`, `last_seen_run_id`, `updated_at`.
Unique: `(connection_id, external_id)` per table.

Canonical payload shapes (JSON examples):

```json
// term
{"name": "2026-27 S1", "start_date": "2026-09-01", "end_date": "2027-01-28", "school_year": "2026"}
// class
{"title": "AI Studio 101", "course_code": "AIS101", "term_external_id": "t-882",
 "school_external_id": "sch-3", "subjects": ["computer-science"], "grades": ["10","11"]}
// enrollment
{"class_external_id": "c-104", "user_external_id": "u-5513", "role": "student",
 "begin_date": "2026-09-01", "end_date": null, "primary": true}
```

Users ride the identity pipeline (§9), not a roster staging table: roster user
records become `ExternalIdentityLink` candidates with
`source='roster'`.

### 6.2 Provisioning map + conflict report

`SyncProfile.options` for roster profiles:
`{"provision": {"class_to": "cohort", "auto_create_cohorts": true,
"instructor_role": "instructor", "student_role": "student",
"on_unenroll": "archive_membership" }}`.

Reconciliation algorithm per run (in `services/roster.py`):

1. Upsert staging rows by `(connection_id, external_id)`; unchanged `raw_hash` ⇒ skip
   (counts as `unchanged`).
2. Rows present in staging but absent from the source snapshot/delta: mark
   `tombstoned` (never delete).
3. Provision pass maps staged rows → Cohort (`settings.integration = {connection_id,
external_id}` backlink), CohortMember, OrgMember. Each mapped write goes through
   the same service functions the UI uses (no bypass of validation).
4. Conflicts append `SyncRecordResult` rows (§11.4) with `conflict_class` ∈
   `ambiguous_identity, duplicate_external_id, missing_reference (enrollment →
unknown class), role_conflict (external says instructor, local manual role
differs), date_invalid`. Conflicted records are **skipped, not guessed** — the
   admin resolves via API (resolution = pick local / pick external / link identity),
   and the next run applies it.
5. Per-connection failure isolation (Clever lesson, S3.1): a run failure in one
   connection never blocks others; the scheduler treats each connection
   independently.

`on_unenroll` policy: `archive_membership` (default — CohortMember archived) or
`ignore`. Never deletes submissions/portfolio data (safety posture §2.4).

## 7. Parts D/E — Talent (ATS/HRIS) & CRM

Same staging pattern, Merge-style canonical models (S4.1), with two hard privacy
rules layered on ADR-015:

- **Candidate data leaves only under consent.** Pushing a candidate/application to an
  external ATS requires an active consent grant (ADR-015 passport consent) covering
  scope `ats_share`; the export mapper runs the same field allowlist used by the
  public passport view — confidential-profile fields (R88 class 1) are structurally
  absent from the mapping input, not filtered after.
- **CRM sync carries zero learner data.** CRM canonical models (`account`, `contact`,
  `deal`) map only to ClientBrief/commercial records; the mapping input builder for
  CRM profiles has no join path to learner tables.

Canonical models (payload JSONB in `intg_talent_records` / `intg_crm_records`,
discriminated by `model` column: `candidate, application, job` / `account, contact,
deal`):

```json
// application (ATS, bidirectional-capable)
{"candidate_external_id": "cand-9", "job_external_id": "job-4",
 "status": "interview", "stage": "tech-screen-2", "applied_at": "2026-10-01T08:00:00Z"}
// deal (CRM)
{"account_external_id": "acct-1", "name": "Q4 cohort pilot", "stage": "proposal",
 "amount": {"currency": "USD", "value": "25000.00"}, "close_date": "2026-12-15"}
```

Field-level source-of-truth for the bidirectional application-status sync (§11.5):
default `{"status": "theirs", "stage": "theirs", "notes": "ours"}` — ATS owns
pipeline position (HubSpot `lifecyclestage` lesson: directional fields get an owner,
never LWW).

## 8. Part J — LTI 1.3 (tool side)

### 8.1 Tables

`intg_lti_registrations`: `id, org_id FK, issuer VARCHAR(500), client_id
VARCHAR(255), auth_login_url, auth_token_url, jwks_url, status, created_at` —
UNIQUE `(issuer, client_id)`. `intg_lti_deployments`: `id, registration_id FK,
deployment_id VARCHAR(255)` — UNIQUE `(registration_id, deployment_id)`; **launches
with an unlisted deployment_id are rejected** (401 `LTI_DEPLOYMENT_UNKNOWN`).
`intg_lti_resource_links`: maps `(deployment_id, resource_link_id)` → platform object
(`kind ∈ skill, project, learning_path`, `target_id`), created by Deep Linking.
`intg_lti_line_items`: AGS lineitem URL per resource link, `grade_sync_enabled
BOOLEAN default false` (grade return is opt-in per link — issue requirement).

### 8.2 Launch validation (every launch; S3.3 checklist as tests)

`state` single-use session-bound (Redis `lti:state:{val}`, 10-min TTL); `nonce`
validated against the session-stored value only (never a request param); `iss`+
`aud` (+`azp` if present) match registration; signature via platform JWKS —
kid-miss triggers one refetch, rate-limited 30s/registration; `iat/exp` ±5 min;
`https://purl.imsglobal.org/spec/lti/claim/version == "1.3.0"`; message type ∈
`LtiResourceLinkRequest, LtiDeepLinkingRequest`; deployment_id in the allowlist.
Launch user → identity resolution §9 with `source='lti'` (subject = `iss|sub` pair);
scoped context: the launch session is restricted to the mapped resource —
it mints a short-lived scoped token (15 min, `aud=lti-launch`, carries
`resource_link_id`), not a full platform session.

AGS grade push: on `project.approved` / `skill.completed` events for a user+resource
with `grade_sync_enabled`, worker POSTs a score to the lineitem using the
client-credentials token (scope `.../lineitem` `.../score`); failures ride the normal
delivery retry ladder; per-link disable stops pushes immediately.

## 9. Part I — Identity resolution

### 9.1 `intg_identity_links`

| column                  | type              | notes                                                                            |
| ----------------------- | ----------------- | -------------------------------------------------------------------------------- |
| id                      | PK ULID           |                                                                                  |
| org_id                  | FK CASCADE        | **tenant-scoped — same external subject in two orgs = two rows, never a bridge** |
| user_id                 | FK users CASCADE  |                                                                                  |
| source                  | VARCHAR(20)       | `sso, scim, roster, lti, ats, manual`                                            |
| connection_ref          | VARCHAR(26)       | sso_connection_id / connection_id / scim_token_id                                |
| subject                 | VARCHAR(500)      | IdP stable subject / provider sourcedId / `iss\|sub`                             |
| external_id             | VARCHAR(255) NULL | SCIM externalId                                                                  |
| email_at_link           | VARCHAR(255)      | snapshot; **never used for re-resolution**                                       |
| created_at / revoked_at |                   | revocation = unlink, reversible                                                  |

UNIQUE `(connection_ref, subject) WHERE revoked_at IS NULL` (partial). Lookup is by
subject, never by email, after the first link (S8.2: email/UPN changes never re-link).

### 9.2 Resolution algorithm (`services/identity.py::resolve`)

Input: `VerifiedExternalIdentity`. Steps, in order, single transaction:

1. Active link for `(connection_ref, subject)` → return that user. (Hot path.)
2. No link, `email_verified=true` at the IdP **and** email domain ∈ this org's
   verified domains → exact-email match against org members:
   - exactly one active member → create link, return user;
   - zero → JIT path if `allow_jit` (create user `status=active`,
     `email_verified=true`, OrgMember `default_role`), else 403 `SSO_NO_ACCOUNT`;
   - more than one (shouldn't happen — users.email unique — but soft-deleted
     collisions can) → queue.
3. Email unverified / domain not verified / any ambiguity → insert
   `intg_identity_match_queue` row `{org_id, source, subject, email, payload,
status=pending}` and fail the login/provision with 403 `IDENTITY_AMBIGUOUS`
   (SSO) or skip-with-conflict (roster). Admin resolves via
   `POST .../identity-queue/{id}/resolve {user_id | "create_new" | "reject"}` —
   resolution creates the link; every resolution is audited.

Race safety: the link insert relies on the partial unique index; on conflict the
loser re-selects (upsert-not-select-then-insert, S8.2). Takeover tests: unverified
email never links; email change at IdP with same subject keeps the same user; same
email different subject queues rather than links; cross-org subject reuse creates
independent links.

## 10. Part H — Mapping profiles (bounded, declarative)

### 10.1 `intg_mapping_profiles`

`id, org_id FK, connection_id FK NULL (null = org-level reusable), name, direction
('inbound'|'outbound'), model VARCHAR(50) (canonical model key), document JSONB,
version INTEGER (bump on every update; SyncProfiles pin a version), created_at`.

### 10.2 Mapping document schema (the whole language — nothing else executes)

```json
{
  "fields": [
    { "target": "title", "path": "classTitle" },
    { "target": "course_code", "path": "course.courseCode", "default": "UNKNOWN" },
    {
      "target": "role",
      "path": "role",
      "enum_map": { "teacher": "instructor", "aide": "instructor", "student": "student" },
      "enum_default": "student"
    },
    { "target": "begin_date", "path": "beginDate", "transform": ["trim", "date_iso"] },
    { "target": "amount", "path": "sum(line_items[].value)" }
  ]
}
```

- `path` is a **JMESPath** expression (not Turing-complete — boundable; the Merge
  precedent S7.1). Evaluation caps: input document ≤ 256 KB, expression length
  ≤ 500 chars, result depth ≤ 10. Compile at document save; invalid expression ⇒
  422 `MAPPING_EXPRESSION_INVALID` naming the field.
- `transform` is a chain from a **closed registry** (in-repo, versioned):
  `trim, lower, upper, date_iso, datetime_iso, to_string, to_int, to_decimal,
split_csv, first, coalesce_empty_null`. Unknown name ⇒ 422 `MAPPING_TRANSFORM_UNKNOWN`.
- `enum_map` exact-match after transforms; miss → `enum_default` if present else the
  record conflicts (`conflict_class=enum_unmapped`).
- Target fields validate against the canonical model's Pydantic schema
  (`extra="forbid"`); non-finite numbers, control chars, oversized strings are
  rejected per-record at this boundary (R86/R87 import-validate rule: **everything
  installation reads is validated at import to its true column bound**).

### 10.3 Preview endpoint

`POST /api/v1/orgs/{org}/integrations/mapping-profiles/{id}/preview` with
`{"samples": [raw_record, ...]}` (≤ 20) → per-sample `{mapped, errors[]}` — same code
path as the engine (one evaluator, structural parity).

## 11. Part G — Sync engine

### 11.1 `intg_sync_profiles`

`id, org_id, connection_id FK, name, model (canonical model key), direction
('pull'|'push'|'bidirectional'), mapping_profile_id + mapping_version, schedule
VARCHAR(50) ('manual' | 'hourly' | 'daily' | cron-ish subset), field_policy JSONB
(§11.5), options JSONB, enabled BOOLEAN, created_at/updated_at`.
UNIQUE `(connection_id, model, direction)`.

### 11.2 `intg_sync_runs`

| column                   | type        | notes                                                                                 |
| ------------------------ | ----------- | ------------------------------------------------------------------------------------- |
| id                       | PK ULID     |                                                                                       |
| profile_id               | FK CASCADE  |                                                                                       |
| status                   | VARCHAR(20) | `queued, running, succeeded, failed, cancelled, partial`                              |
| trigger                  | VARCHAR(20) | `schedule, manual, webhook, backfill`                                                 |
| cursor_in                | JSONB       | state given to this run (Airbyte: only destination-confirmed state is ever passed in) |
| cursor_out               | JSONB       | state after; **written only after records commit** (§11.3)                            |
| stats                    | JSONB       | `{read, created, updated, unchanged, tombstoned, conflicts, errors}`                  |
| error                    | JSONB NULL  | `{class, message_trunc}`                                                              |
| started_at / finished_at |             |                                                                                       |
| heartbeat_at             | timestamptz | worker liveness; a run stale >10 min is reaped to `failed` (crash-retry pin, R85)     |

Index `ix_intg_runs_profile (profile_id, started_at DESC)`. Only one
`queued|running` run per profile (partial unique on `profile_id WHERE status IN
('queued','running')`) — a second trigger returns the existing run (idempotent).

### 11.3 Cursor & checkpoint algorithm (Airbyte rules, S6.1)

```
state = run.cursor_in  # e.g. {"stream":"enrollments","updated_since":"2026-10-09T00:00:00Z","page":null}
for batch in connector.read(state):           # ≤500 records per batch
    with db.begin():                          # one txn per batch
        results = apply_mapping_and_write(batch)
        state = batch.next_state              # provider cursor/page token
        run.cursor_out = state                # SAME txn as the writes ⇒
        run.stats += results.counts           # "destination-confirmed" by construction
    heartbeat()
```

- Crash between batches re-runs from the last committed `cursor_out`; writes are
  idempotent upserts on `(connection_id, external_id)` ⇒ at-least-once + dedup.
- Checkpoint cadence target: every batch (≪ Airbyte's 30-min SLO).
- Backfill = run with `cursor_in = {}`; tombstone detection only runs on full
  snapshots (`trigger='backfill'` or provider sends full pages), never on
  incremental deltas (an absent record in a delta is not a delete).
- Rate limits/429: exponential backoff within the run (1s·2ⁿ, max 5 retries, then
  run `failed` with `error.class='rate_limited'`); provider `Retry-After` honored.
- Pagination tokens live inside `cursor_out` so resume continues mid-collection.

### 11.4 `intg_sync_record_results` (record-level observability + conflicts)

`id, run_id FK CASCADE, external_id, model, outcome ('created','updated','unchanged',
'tombstoned','conflict','error'), conflict_class VARCHAR(40) NULL, detail JSONB
(small, no PII beyond ids), resolved_by FK users NULL, resolved_action VARCHAR(20)
NULL, created_at`. Index `(run_id, outcome)`. Only non-`unchanged` outcomes get rows
(unchanged is a counter) — bounds table growth.

### 11.5 Bidirectional conflicts (S6.2)

`field_policy` JSONB on the profile: `{"<field>": "ours" | "theirs" | "most_recent"
| "prefer_ours_unless_blank"}` + `"_default": "theirs"`. Rules:

- A side never overwrites a field it doesn't own; `most_recent` compares our
  `updated_at` vs provider's modified timestamp (both required, else conflict row
  `conflict_class=clock_unresolvable`).
- **Echo suppression**: outbound writes record `{external_id, fields_hash,
written_at}` in `options.last_outbound` (per record, in `intg_*_records.payload`
  sidecar `_sync` key); an inbound change whose mapped field-hash equals our last
  outbound hash within 24h is dropped as an echo (`outcome=unchanged`).
- Same-field both-sides-changed with policy `most_recent` and equal timestamps ⇒
  conflict row, no write (deliberate: ties are human decisions).

## 12. Part F — Event mesh

### 12.1 `intg_events` (canonical, append-only, CloudEvents 1.0)

| column     | type              | notes                                                                                       |
| ---------- | ----------------- | ------------------------------------------------------------------------------------------- |
| id         | VARCHAR(26) PK    | ULID — doubles as CloudEvents `id` (idempotency key at every hop)                           |
| org_id     | FK CASCADE        |                                                                                             |
| type       | VARCHAR(100)      | `com.openskill.{entity}.{action}.v{N}` — immutable once published; breaking schema ⇒ new vN |
| source     | VARCHAR(200)      | `/orgs/{org_id}`                                                                            |
| subject    | VARCHAR(255) NULL | entity id                                                                                   |
| time       | timestamptz       |                                                                                             |
| dataschema | VARCHAR(200)      | `/schemas/events/{type}.json` (in-repo, versioned)                                          |
| data       | JSONB             | versioned aggregate snapshot                                                                |

Index `(org_id, type, time DESC)`. Emission: `facade.emit_event(db, org_id, type,
subject, data)` inserts the row **and** a `cp_outbox` message (`topic=
'intg.event.created'`) in the caller's transaction — reuses ADR-014 outbox verbatim.
Initial catalog (issue Part F list): `learner.enrolled, skill.completed,
project.approved, brief.created, client.accepted, credential.issued,
placement.started, invoice.finalized, ecosystem.change_verified` (each `.v1`), plus
fabric-internal `integration.connection.unhealthy, integration.sync.completed,
integration.delivery.exhausted, org.sso.login, org.breakglass.login,
org.scim.deprovisioned`.

### 12.2 Delivery (`intg_event_deliveries` + `intg_delivery_attempts`)

Deliveries fan out: outbox handler matches the event against active
`webhook_subscriptions` (existing table; `events` array supports exact type or
prefix `com.openskill.project.*`) and inserts one delivery row per match:
`id, event_id FK, subscription_id FK, status ('pending','delivering','succeeded',
'exhausted','cancelled'), attempt_count, next_attempt_at, created_at`. Attempts:
`id, delivery_id FK, status_code INT NULL, error VARCHAR(200) NULL, latency_ms,
attempted_at` — the per-attempt log is the observability surface (Svix S5.2).

Signing (Standard Webhooks, byte-for-byte): headers `webhook-id` (event ULID),
`webhook-timestamp` (unix seconds), `webhook-signature: v1,{base64(hmac_sha256(
secret, f"{id}.{timestamp}.{body}"))}`; during secret rotation both old+new secrets
sign ⇒ two space-separated `v1,` entries. Subscription secrets upgrade in place:
`secret` column stays, new nullable `secret_prev` + `secret_rotated_at` (prev honored
7 days). Receiver guidance documented: verify raw body, 5-min timestamp window.

Retry ladder (Svix): attempt offsets `[0s, 5s, 5m, 30m, 2h, 5h, 10h, 10h]` + full
jitter ±10%; HTTP timeout 15s; success = any 2xx. After attempt 8 ⇒ status
`exhausted`, emit `integration.delivery.exhausted` (alertable event, not just a log).
**Auto-disable**: a subscription whose every delivery over the trailing 5 days
exhausted flips `active=false` + event. Replay: `POST .../deliveries/{id}/replay`
clones to a fresh delivery (new attempts, same payload+id ⇒ receiver dedup still
works); bulk replay by subscription+time-range for post-outage recovery, capped 1000.

Dispatch goes through `EgressClient` (§14.1) — URL re-validated at **every attempt**
(DNS rebinding, S8.1).

## 13. Part M — Connector SDK boundary

In-repo only (v1; marketplace connectors are issue #44 territory). Interface
(`services/connectors/base.py`):

```python
class Connector(Protocol):
    key: str                      # == intg_providers.key
    capabilities: frozenset[str]  # e.g. {"roster.read"} — must ⊆ provider row's list
    async def ping(self, ctx: ConnCtx) -> None: ...                 # health/credential check
    async def read(self, ctx: ConnCtx, model: str, state: dict) -> AsyncIterator[Batch]: ...
    async def write(self, ctx: ConnCtx, model: str, records: list[dict]) -> list[WriteResult]: ...
```

`ConnCtx` exposes `config`, a **scoped token accessor** (decrypts inside the call,
never returns the blob to the engine), and the EgressClient — a connector cannot
construct its own HTTP client. Capability enforcement at **binding time and run
time** (R82 runtime re-check): the sync engine refuses a profile whose
`model+direction` demands a capability the connector (at the pinned provider
version) doesn't declare — `409 CAPABILITY_MISSING` — and re-checks on every run
start (catalog may have changed). Registry: `CONNECTORS: dict[str, Connector]`
checked against `intg_providers` in CI (every provider key has a connector and
vice versa; capability sets equal).

v1 connectors: `oneroster` (pull roster), `generic_webhook` (push events — already
the delivery path), `csv_import` (§bulk, file-based), `scim_idp`/`saml_idp`/
`oidc_idp`/`lti_platform` (protocol endpoints, not engine connectors), `warehouse_s3`
(§export). ATS/CRM concrete connectors land in later phases behind the same
interface.

## 14. Part O — Security backbone

### 14.1 `EgressClient` (every outbound byte)

- Resolve hostname → validate **every** resolved IP against the deny set (127/8,
  10/8, 172.16/12, 192.168/16, 169.254/16, 100.64/10, ::1/128, fc00::/7, fe80::/10,
  IPv4-mapped IPv6, 0.0.0.0/8) → connect to the validated IP with SNI/Host pinned to
  the hostname (no re-resolution window) — per dispatch, not per registration.
- Schemes http/https only (https-only outside APP_ENV=test); redirects **not**
  followed (3xx is a terminal response; webhook receivers must answer at the
  registered URL); response body capped 1 MB; connect/read timeouts 5s/15s.
- Private-range allowance exists solely under `APP_ENV=test` (E2E hits localhost —
  R79 pattern), controlled by `settings.egress_allow_private`.
- Unit matrix: decimal/hex IPs, `localhost.evil.com`, rebinding mock (first resolve
  public, second private — must not re-resolve), IPv6-mapped forms, 30x downgrade.

### 14.2 Cross-cutting

- All inbound schemas `extra="forbid"` (R85); every staged/imported field validated
  to its true column bound before any DB write (R86/R88) — the global DBAPIError
  backstop stays as backstop, not primary defense.
- Admin mutations (connections, mappings, SSO config, SCIM tokens, domain claims,
  resolution decisions, replays) append `intg_events` audit rows with actor id.
- OAuth scopes requested per connector are the **minimum** declared in the provider
  row (`config_schema` documents them); never `offline_access`+wildcards by default.
- IDOR tests: every `{org_id}`-scoped resource × foreign org id ⇒ 404 (read AND
  write AND replay/resolve subactions) — extends the R88 uniform-404 suite.

## 15. API surface (all under `/api/v1`, `{data}`/`{data, meta}` envelopes)

Org-scoped admin (require_org_member(admin) unless noted):

```
GET/POST        /orgs/{org}/integrations/connections            · GET/PATCH/DELETE /{id}
POST            /orgs/{org}/integrations/connections/{id}/credentials     (write-only)
POST            /orgs/{org}/integrations/connections/{id}/ping
GET/POST        /orgs/{org}/integrations/domains                · POST /{id}/verify · DELETE
GET/POST        /orgs/{org}/integrations/sso-connections        · GET/PATCH/DELETE /{id}
POST            /orgs/{org}/integrations/sso-connections/{id}/test        (testing status launch)
GET/POST        /orgs/{org}/integrations/scim-tokens            · DELETE /{id}   (token shown once)
GET/POST        /orgs/{org}/integrations/mapping-profiles       · GET/PATCH /{id} · POST /{id}/preview
GET/POST        /orgs/{org}/integrations/sync-profiles          · GET/PATCH/DELETE /{id}
POST            /orgs/{org}/integrations/sync-profiles/{id}/run           (manual trigger)
GET             /orgs/{org}/integrations/sync-runs              · GET /{id} · POST /{id}/cancel
GET             /orgs/{org}/integrations/sync-runs/{id}/records?outcome=conflict
POST            /orgs/{org}/integrations/records/{id}/resolve
GET             /orgs/{org}/integrations/identity-queue         · POST /{id}/resolve
GET             /orgs/{org}/integrations/events?type=&since=    (audit + mesh browse)
GET             /orgs/{org}/integrations/deliveries?status=     · GET /{id} (attempts)
POST            /orgs/{org}/integrations/deliveries/{id}/replay · POST /deliveries/replay-bulk
GET/POST        /orgs/{org}/integrations/lti/registrations      · deployments · resource-links
GET/POST        /orgs/{org}/integrations/imports                (§16) · GET /{id} · POST /{id}/commit
GET             /orgs/{org}/integrations/imports/{id}/errors.csv
GET/POST        /orgs/{org}/integrations/export-streams         · GET /{id}/runs
```

Protocol endpoints (unauthenticated-or-protocol-auth, outside org prefix):
`/sso/saml/metadata`, `/sso/saml/acs/{conn_id}`, `/sso/oidc/callback`,
`/sso/login?email=` (domain-based IdP discovery → redirect), `/scim/v2/*` (bearer),
`/lti/login`, `/lti/launch`, `/lti/jwks`, `/lti/deep-linking/return`.

Error codes introduced (machine codes, `{error:{code,message}}`): `PROVIDER_NOT_FOUND,
PROVIDER_DISABLED, CONNECTION_NOT_FOUND, CONNECTION_CONFIG_INVALID,
CONNECTION_NAME_TAKEN, EGRESS_BLOCKED, DOMAIN_ALREADY_VERIFIED, DOMAIN_NOT_ELIGIBLE,
DOMAIN_VERIFY_FAILED, SSO_REQUIRED, SSO_NO_ACCOUNT, SSO_ASSERTION_INVALID,
BREAK_GLASS_UNVERIFIED, IDENTITY_AMBIGUOUS, MAPPING_EXPRESSION_INVALID,
MAPPING_TRANSFORM_UNKNOWN, CAPABILITY_MISSING, SYNC_RUN_ACTIVE, SYNC_RUN_NOT_CANCELLABLE,
LTI_DEPLOYMENT_UNKNOWN, LTI_LAUNCH_INVALID, IMPORT_DRY_RUN_STALE, IMPORT_TOO_LARGE,
EXPORT_FIELD_NOT_ALLOWED, DELIVERY_NOT_REPLAYABLE`.

## 16. Parts K/L — Bulk import & warehouse export

### 16.1 Import (`intg_import_jobs`, S8.3)

`id, org_id, kind ('roster'|'users'|'opportunities'), template_version INT, mode
('atomic'|'partial'), status ('validating','previewed','committing','succeeded',
'failed','partial','stale'), file_key (S3, 50 MB cap ⇒ IMPORT_TOO_LARGE),
fingerprint CHAR(64) (SHA-256 of file + template_version + relevant org state rev),
stats JSONB, dry_stats JSONB, idempotency_key VARCHAR(100) NULL UNIQUE-per-org,
created_by, created_at`. Errors in `intg_import_row_errors (job_id, row_number
1-indexed-plus-header, column, code, message)` — capped 10 000 rows, error CSV
endpoint streams original row + `error` column with **CSV-injection sanitization**
(`=+-@` cell prefixes get `'`-escaped).

Pipeline: upload → `validating` (streamed parse: BOM/CRLF tolerant, header-based
mapping, missing required column fails the file; batched lookups per 500-row chunk)
→ `previewed` with `dry_stats {valid, errors, creates, updates, skips}` → **commit
requires the same fingerprint** or 409 `IMPORT_DRY_RUN_STALE` → commit executes the
identical validation+write code with the transaction policy: `atomic` = one txn,
any error ⇒ rollback + `failed`; `partial` = 500-row txn chunks, failed chunk
replayed row-by-row so only truly bad rows fail; rows carry caller `external_id` ⇒
re-upload idempotent (matched-unchanged skip / drifted update).

### 16.2 Warehouse export (`intg_export_streams` / `intg_export_runs`, S8.4)

Stream: `id, org_id, connection_id (warehouse_s3), dataset ('enrollments'|
'skill_outcomes'|'project_outcomes'|'placements'|'events'), field_allowlist JSONB
(explicit list — serializer refuses any field not listed: EXPORT_FIELD_NOT_ALLOWED
at config time, and the writer selects ONLY allowlisted columns — R82 total-coverage
test generates the field universe from the dataset schema and asserts the default
template ⊆ allowlist), anonymize JSONB ({field: 'hash'|'drop'} — learner ids hash
with per-org salt by default), schedule, cursor JSONB, enabled`. Run: incremental
NDJSON parts to `exports/{org}/{dataset}/{run_ulid}/part-N.ndjson.gz` + `manifest.json
{cursor_from, cursor_to, row_count, schema_version, generated_at}` — freshness is
first-class (Stripe Data Pipeline). Tenant boundary enforced in the extraction query
(org_id predicate injected by the facade, not by the connector).

## 17. Delivery phases (each independently shippable)

1. **P1 Fabric core**: providers/connections/credentials, EgressClient, facade,
   worker skeleton, admin API + IDOR/404 suite.
2. **P2 Event mesh**: intg_events + emit facade, deliveries/attempts, Standard-Webhooks
   signing, retry/DLQ/replay/auto-disable, wire the 9 catalog events from existing
   services.
3. **P3 SSO**: org domains + DNS verify cron, OIDC then SAML, enforce_sso +
   break-glass, login audit.
4. **P4 SCIM**: tokens, Users/Groups, deprovision-revokes-sessions, scim2-tester CI.
5. **P5 Mapping + sync engine**: mapping documents/preview, SyncProfile/Run/records,
   cursor-checkpoint loop, conflict surfaces.
6. **P6 Roster**: canonical staging, oneroster connector, provisioning + conflict
   resolution, per-connection isolation.
7. **P7 LTI**: registrations/launch/deep-linking/AGS opt-in grade push.
8. **P8 Bulk import** (roster/users templates). **P9 Warehouse export.**
9. **P10 Talent/CRM**: canonical models + field policies + consent-gated ATS push
   (concrete vendor connectors as capacity allows).
10. **P11 Admin UI** (Part N): connection setup wizard (config_schema-driven), mapping
    editor + preview, sync history/conflicts, delivery log + replay, health dashboard.

## 18. Testing plan

- Unit: EgressClient matrix (§14.1), SAML validation vectors (unsigned/SHA-1/XSW
  clone/audience/replay/cross-tenant cert), SCIM PATCH leniency table, mapping
  evaluator caps, cursor-resume property tests (crash at any batch ⇒ no loss, no
  dupes — hypothesis), echo-suppression, retry-ladder scheduling math.
- Protocol conformance: scim2-tester against the test app; recorded OneRoster
  fixture pages (pagination + delta + full-snapshot tombstones); LTI launch vectors
  incl. nonce-echo and unlisted deployment.
- Security suite extensions: uniform-404 IDOR over every new resource incl.
  subactions; credential-echo grep (response models never contain ciphertext/token
  fields); R82-style field-universe tests for export allowlists and SCIM/webhook
  response models; break-glass audit presence.
- E2E (APP_ENV=test, live API): directory → SSO login → SCIM provision → roster
  sync → cohort provision → project approval → event delivery (inline outbox) →
  AGS push → export run — the issue's acceptance flow.

## 19. Known edges & explicit decisions

- **SAML SP (P3b) uses signxml**, not python3-saml/pysaml2: pure-python XML-DSIG
  avoids the xmlsec1 native dependency, and the verifier returns ONLY the signed
  subtree — the XSW family (unsigned sibling assertions) cannot be consumed by
  construction. SAML mandates exclusive c14n; inclusive-c14n signatures break once
  wrapped (pinned by test). IdP-initiated (unsolicited) responses are rejected in v1.
- **No /Bulk SCIM in v1** (advertised unsupported); Entra works without it.
- **SCIM payload layer is hand-rolled** (P4 decision, supersedes the §5.3
  scim2-models recommendation): the production rules that matter — lenient Entra
  PATCH parsing, deactivate≡DELETE with session sweep, delta membership,
  reactivation-not-409 — fight strict model libraries, and the resource subset is
  tiny. Every rule is pinned by a test; scim2-tester conformance runs are deferred
  until the dependency earns its keep.
- **No FIFO delivery guarantee** (Svix lesson): consumers get `time` + replay; we
  document at-least-once unordered.
- **OneRoster push (gradebook) deferred** to the LTI AGS path — one grade-return
  mechanism first.
- **SAML SP metadata is per-environment static**; per-connection ACS path carries the
  connection id (not a secret — security rests on cert pinning, not URL secrecy).
- **JIT default_role ceiling**: instructor. Owner/admin always human-granted.
- **Clock skew**: SAML 90s, LTI ±5 min, `most_recent` field policy requires both
  timestamps (conflict otherwise) — no wall-clock tie-breaking (clock_timestamp
  lesson from ADR-017).
- **Egress in tests**: private ranges allowed only under APP_ENV=test via settings —
  the test asserting the flag is false in prod config is part of P1.
- **Webhook secret size**: existing `secret` column VARCHAR(64) holds base64 32-byte
  keys; `whsec_` prefix added at the API presentation layer to match Standard
  Webhooks tooling.
- **invoice.finalized routing (P10 decision)**: the tenant fact fans out to each of
  the tenant's orgs as a PRIVACY-SAFE notification — invoice id + tenant id only,
  never amounts (org admins are not tenant billing admins). Org-level automation can
  react; billing figures stay on the control plane. All other
  catalog events are wired (P2b): learner.enrolled, skill.completed, project.approved,
  brief.created, client.accepted at their domain sites; credential.issued,
  placement.started, ecosystem.change_verified (mapped from ecosystem.change) and
  every other legacy webhook event via the trigger_event mirror.
- **Staging is one generic table** (P5 decision, supersedes §6.1's per-entity tables):
  `intg_staged_records` discriminated by `model` — the engine, tombstone pass and
  conflict reporting are written once and cover roster/talent/CRM uniformly.
- **Unenroll policy is `remove_membership`, not `archive_membership`** (P6): the
  product CohortMember model has no archived state; removal never touches
  submissions/portfolio data (§2.4 holds).
- **Roster user trust**: SIS data arrives over the org's authenticated connection —
  the org vouches for roster emails the way an IdP does (same trust root as SCIM),
  so roster identity resolution treats them as verified; ambiguity still queues.
- **LTI AGS lineitem URLs are egress-screened at launch**: a platform asserting a
  private-range lineitem endpoint is logged and ignored, never stored.
- **Provider version upgrades**: explicit `POST /connections/{id}/upgrade` re-validates
  config against the new config_schema and re-checks capabilities — may surface
  CAPABILITY_MISSING, never silent.

- **R44 — retention**: nightly 03:52 sweep ages out TERMINAL deliveries
  (90d, attempts cascade), events (180d), terminal sync runs (180d, record
  rows cascade) and import row errors (180d) in 10k-id batches with
  per-batch commits. Pending work never ages out. Connection health decays
  via the half-hourly ping sweep (R41) with transition alerts.

- **R42 — OIDC Back-Channel Logout 1.0 (RP)**: POST
  /sso/oidc/backchannel-logout/{connection_id} accepts the IdP's
  logout_token (same discovery→JWKS trust chain as id_tokens; events member
  required; nonce prohibited; jti single-use via the login-state replay
  cache; iat freshness 2×skew) and revokes every refresh token of the
  linked user. Unknown subject returns clean 200 — no oracle. SAML SLO
  remains deferred (front-channel only; rarely deployed).

- **R20/R23 decision — unlink does NOT revoke sessions**: unlinking an
  external identity only severs the mapping (reversible; audit row kept).
  The platform account and its sessions stand — offboarding is SCIM
  deactivation or member removal, both of which sweep refresh tokens.
  accept_theirs adjudication carries a staleness guard (409 when the staged
  field moved since the conflict was recorded).

- **R124 — bidirectional direction**: the enum accepted "bidirectional" but
  execute_run routed it to pull-only (push is talent.application-specific and
  a profile carries ONE model) — a silent half-implementation. Now rejected
  at creation with guidance to pair a pull + a push profile; Part G
  bidirectional is achieved by that pairing, not a single mixed profile.

- **R120/R121 — CRM (Part E)**: generic CRM READ connector ships
  (accounts/contacts/deals → canonical crm.* models, API-key + pagination,
  read-only). CRM→ClientBrief AUTO-provisioning is DELIBERATELY NOT built:
  a ClientBrief requires human-authored objective, project_type and
  evaluation_criteria that a CRM deal does not carry — auto-creating briefs
  would fabricate those fields and pollute the production pipeline. The
  staged crm.* records are available for reporting/warehouse export and a
  MappingProfile can target them; linking a deal to an EXISTING brief is an
  explicit admin action (no learner data crosses into the CRM either
  direction). This is the privacy-safe reading of "map CRM deals/accounts
  to Client Briefs ... without leaking internal learner data."

- **Deferred (explicit, R311 audit)**: §5.2's "WebAuthn-or-TOTP required"
  clause for break-glass members is NOT implemented — the platform has no
  MFA infrastructure at all (tracked as Gap #181 under the talent epic),
  so building WebAuthn/TOTP under issue #43 would be an unscoped
  cross-epic auth feature. Compensating controls in place: max-2 designee
  cap (race-proof, R260), owner-only designation, every break-glass login
  audited + mesh-emitted, and the 90-day freshness gate on manual cert
  rotation (R311). Revisit when platform MFA lands.
- **Deferred (explicit, as of R19)**: import template kinds `roster`
  (SHIPPED R129) and `opportunities` (SHIPPED R131 — draft-only postings,
  employer-profile gate, idempotent by lower(title)); LTI NRPS
  (SHIPPED in R49 as membership pre-provisioning — launch captures the
  namesroleservice claim, admin-triggered sync pages the roster through
  identity resolution with the instructor/student role map; no cohort
  writes, placement stays a launch concern); SAML idp_metadata_url auto-polling (SHIPPED R51: daily 05:37 sweep + manual refresh endpoint — hardened parse, signing-keys only, pem-diff rotation detection; the R19 expiry sweep still alerts 30 days out as the backstop); per-key
  selection of the events `data` payload in warehouse exports (SHIPPED R130:
  explicit `data.<key>` allowlist entries, events dataset only, capped at 20,
  hash/drop anonymize supported; the whole payload remains unexportable); CRM outbound
  extractors (models + engine support exist; vendor connectors are issue #44
  marketplace territory).

## 20b. Part O security checklist (final audit, R100-R104)

| Requirement                        | Evidence                                                                                                                                                        |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Encrypted secrets                  | Fernet envelopes, write-only (`has_client_secret`); SCIM tokens hashed; LTI tool keys encrypted                                                                 |
| SSRF-safe outbound                 | single-egress lint test; resolve→validate-all-IPs→pin dial; mixed-set refusal; NRPS next-links + metadata endpoints re-screened                                 |
| Allowlisted callback/redirect URIs | R101/R102: every redirect URI derived from `public_base_url`, never the Host header (hostile-Host guard test); SSO deep links relative-path screened both sides |
| Webhook signature verification     | Standard Webhooks `v1,HMAC-SHA256(id.ts.body)`; 7-day co-sign rotation; byte-exact archive keeps receiver checks stable                                         |
| Replay protection                  | OIDC state/nonce single-use; SAML assertion-id + InResponseTo caches; back-channel jti cache; SLO signed-only                                                   |
| Least-privilege OAuth scopes       | R104 guard test pins roster.readonly / AGS score / NRPS membership.readonly / `openid email profile`                                                            |
| Cross-tenant IDOR tests            | uniform-404 walls service- and API-level; live E2E walls 8 list surfaces with a second real user                                                                |
| Field-level export allowlists      | allowlist-BUILT projection (narrowed-list leak killer), org-salted hashing                                                                                      |
| Audit logs for admin mappings      | R100: 16 registered intg.* actions across mappings/profiles/SSO/credentials/SCIM tokens/conflict adjudication                                                   |
| Safe deprovision                   | SCIM deactivate≡DELETE sweeps refresh tokens incl. rotation predecessors; back-channel + SLO sweep sessions; unenroll never deletes work product                |

## 20a. Issue #43 acceptance-criteria mapping (final audit)

| Criterion                                | Evidence                                                                                                                                                                                                                                                                     |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Enterprise SSO + SCIM                    | OIDC RP + SAML SP + metadata rotation + enforced-SSO/break-glass + back-channel logout; /scim/v2 incl. /Bulk, Entra dialects, safe deprovision (session sweep)                                                                                                               |
| Canonical sync engine across categories  | SyncProfile/SyncRun engine: cursors, idempotent claims, pagination, backfill, tombstones, conflicts+adjudication, echo suppression; connectors: OneRoster (roster), generic REST (any), generic ATS (talent push), generic webhook (mesh)                                    |
| SIS/LMS roster provisions cohorts safely | staged roster → RosterProvisioningService: never-guess conflicts, role ceiling, unenroll policies; NRPS pre-provisioning                                                                                                                                                     |
| ATS/HRIS/CRM respect privacy/consent     | push engine gated by ats_share ConsentLog; consent_missing conflicts; warehouse allowlists + org-salted hashing                                                                                                                                                              |
| Event mesh with replay/dead-letter       | CloudEvents + Standard-Webhooks signing, Svix ladder, exhausted=dead-letter + first-class event, replay endpoint, auto-disable, test-send, response snippets                                                                                                                 |
| Mappings declarative, non-executable     | JMESPath + fixed transform table, compile-at-save, caps; no user code paths                                                                                                                                                                                                  |
| Warehouse exports incremental + governed | cursor advances only on success; allowlist-BUILT projection; manifest freshness; schedules + retention                                                                                                                                                                       |
| Connector health/conflicts observable    | health summary endpoint + hub strip, half-hourly ping sweep + unhealthy transitions, per-subscription stats, record-level conflict rows + UI adjudication                                                                                                                    |
| Full E2E chain                           | tests/e2e_integration_lifecycle.py: 62 live-HTTP checks (register→domain→connection→SCIM→mapping→sync→mesh delivery→replay→bulk-replay→export→CSV/JSON+roster+opportunities imports→IDOR walls) + acceptance-chain DB test                                                   |
| Browser journey (every admin create)     | tests/browser_e2e_integrations.mjs: 65 checks — register→org→all five pages, every create form driven (connection/domain/SCIM token/SSO/LTI/subscription/stream/import), negatives, shown-once-gone-on-reload, outsider lockout, 390px no-overflow, a11y names, console gate |
| Realistic scale bounds                   | tests/e2e_scale_smoke.py: 22 checks — 300 SCIM users, full-directory paging, eq-filter point lookup, 50-user bulk deactivate, 500-row CSV import commit, 200 events→2 subs→400 live deliveries, all wall-clock bounded                                                       |
| CI enforcement                           | ci.yml: fabric Playwright sweep (sweep-integrations.spec.ts) + e2e-integration-fabric live-HTTP job + ruff format gate; contract guards (web→API path+method, sweep source-scan, ops caps table, doc test refs) run in the backend suite                                     |

## 20. Implementation log (newest-first; marathon rounds R7+ on 2026-10-11)

- **R421 (fourteenth window, mutation)**: AST-mutating `_validate_user_rows`
  (bulk_import, 9 mutants) left 5 survivors: `Or->And` on the email reject
  chain (a non-empty, short, NUL-free but format-invalid email would have
  passed validation under the mutant — the regex disjunct was never exercised
  in isolation), the 255-char email length boundary, and the 100/200-char
  display/raw-echo truncation caps. Added
  `test_validate_user_rows_reject_disjuncts_and_truncation_boundaries`
  pinning each disjunct independently and both caps exactly; re-run 9/9
  killed. Assertion-gap class (R417/R418 family), no production change.
- **R420 (fourteenth window, closing regression)**: full wave after
  R408-R419 — 12/12 chunks = 10,808 backend tests; battery 390;
  lifecycle 77/77; scale 37/37; storm 8/8; fuzz 399/seed zero-5xx;
  adversarial 178/0; walk 65/65; a11y 5/5; web 766; all 10 drills green
  (EXPLAIN flagged=0). Window-14 theme was depth over breadth on an
  already-converged fabric: property SOUNDNESS (SSRF), three shipped
  write-path coverage fills (push/AGS/fan-out), two race-recovery
  branches, and mutation-testing the SSRF/SCIM/webhook-crypto cores to
  convert "executed" into "asserted" — one real bug (R409 SCIM member
  case). head intg21a00021; not merged, no PR.
- **R419 (fourteenth window, \_deprovision mutation-tight)**: mutation-tested
  the SCIM _deprovision last-owner guard (R330, access-control-critical) —
  6/6 mutants killed, 0 survivors; the guard that stops an IdP from
  deactivating an org's last owner is fully assertion-covered, not just
  executed. Harness-safety note added to memory: NEVER interrupt the AST
  mutation harness mid-run — its source restore is in a `finally`, so a
  TaskStop leaves the target file mutated (recovered here with `git
checkout` + a scoped, fast test cmd that completes within the cap).
- **R418 (fourteenth window, mutation-killing the co-sign window)**:
  mutation testing build_delivery_headers surfaced that the webhook
  secret-rotation co-sign grace (previous secret co-signs for 7 days so
  receivers can roll keys) was executed but under-asserted — And→Or,
  LtE→Lt and window-arithmetic mutants survived. Added a boundary test:
  two sigs just inside / one just outside the window, one when
  secret_prev is unset, one when rotated_at is missing (both guards
  required), and inclusion EXACTLY at the 7-day edge. All mutants killed
  (0 survivors). The domains email-slice mutant (rsplit maxsplit 1→2) is a
  true equivalent — `[-1]` is the last segment regardless of maxsplit.
- **R417 (fourteenth window, mutation-testing the SSRF + SCIM parsers)**:
  ran the AST mutation harness against validate_egress_url/_is_forbidden_ip
  and SCIM _normalize_path/_coerce_active. 5 mutants survived = real
  assertion gaps the line-coverage missed: the egress URL-length boundary
  (>MAX_URL_LEN vs >=) and the SCIM URN-prefix strip offset (len+1). Added
  killing tests: a boundary URL at exactly 500 chars passes / 501 refused,
  and a fully-qualified URN path strips to the exact bare attribute
  (case-preserved per R409). Re-run confirms them killed; the two
  remaining security mutants are genuine EQUIVALENTS (the https/80 default
  port only feeds the allowlist, where 443 and 80 are both admitted —
  mutating the default changes no admit/deny outcome). Lesson: line
  coverage says "executed", mutation says "asserted".
- **R416 (fourteenth window, backchannel-logout reject matrix)**: running
  the fuzzer against a COVERAGE-instrumented server proved phase 9b's
  hostile logout_tokens die at the OIDC discovery egress fetch (fake
  issuer host won't resolve) BEFORE reaching JWT verification — the
  R394 lesson recursing one layer deeper: a route the fuzz "reaches" can
  still shield a parser behind an earlier network step. Completed the
  backchannel-logout reject matrix as unit tests (injected discovery +
  JWKS): alg≠RS256 (HS-confusion), unknown kid, unparseable header, and
  tampered-signature all refuse cleanly. sso_oidc backchannel branches
  now fully covered.
- **R415 (fourteenth window, mid-window regression + close)**: full wave
  after R408-R414 — 12/12 chunks = 10,800 backend tests; battery 384;
  lifecycle 77/77; scale 37/37; storm 8/8 (p95 elevated under post-wave
  machine load, SLO held); fuzz 399/seed zero-5xx; adversarial 178/0;
  walk 65/65; a11y 5/5; web 766; all 10 drills green (EXPLAIN flagged=0 —
  intg20/intg21 indexes holding). This window's theme: property-based
  SOUNDNESS (not just totality) on the SSRF gate (5,500-IP sweep,
  0 bypass) + filling three shipped-write-path coverage holes
  (_execute_push, AGS push_score, gradeable fan-out) + two race-recovery
  branches (R409 case bug was the one real defect; R414 the identity
  loser-recovery). head intg21a00021; not merged.
- **R414 (fourteenth window, identity first-login race recovery)**:
  `_link`'s loser-recovery branch (a concurrent first login already
  committed the (connection_ref, subject) link, so the second INSERT
  violates the partial unique index inside the savepoint and the except
  re-reads the winner instead of 500ing) had never executed in tests.
  Driven deterministically with two one-per-request sessions: winner
  commits the link, loser _links the same identity → INSERT collides →
  recovery returns the winner's link, exactly one link survives. Only the
  defensive re-raise (unrecoverable case) stays uncovered, correctly.
- **R413 (fourteenth window, gradeable-event fan-out coverage)**:
  `handle_gradeable_event` — the worker hook that turns an internal
  gradeable event into AGS pushes (the automation that makes
  grade-passback actually fire) — was uncovered. Test covers: unknown
  event type → 0, missing target/user → 0, a matched grade-enabled link →
  one push, score clamped into [0,100] (final_score 150 → 100), and a
  non-numeric score → 0.0. lti_ags coverage 60%→79%.
- **R412 (fourteenth window, AGS grade-passback coverage)**: `push_score`
  (LTI AGS grade → the LMS /scores endpoint) was another uncovered
  outbound WRITE path. New test launches to JIT a mapped user, then
  exercises every branch: grade-sync-disabled returns False with no call,
  a never-launched user (no subject) returns False with no POST, the happy
  path POSTs a well-formed AGS Score (userId/scoreGiven/FullyGraded) to
  <lineitem>/scores and returns True, and an LMS 4xx refusal returns
  False. lti_ags coverage 44%→60%.
- **R411 (fourteenth window, push-execution coverage)**: a coverage sweep
  found `_execute_push` (talent.application → external ATS/HRIS, ~150
  lines) had ZERO execution coverage — only the preview rejection was
  tested, so the whole outbound write cycle shipped unexercised. New DB
  test drives it against a fake ATS: consented rows push (outcome=updated
  - echo-suppression sidecar written), an un-consented row is a
    consent_missing conflict (never sent), an ATS-rejected row is an error,
    a re-run with identical payloads skips unchanged, and the run finishes
    `partial` when conflicts/errors exist. sync_engine coverage 73%→84%.
- **R410 (fourteenth window, parser totality nets)**: hypothesis totality
  properties over three more security-critical parsers — SCIM
  `_coerce_active` (bool/None over arbitrary nested PATCH values,
  recursion-safe), SAML `_parse_time` (aware datetime or clean ValueError,
  never TypeError/500 on the ACS), and the webhook `sign_payload`
  (total + deterministic, confirmed emitting the Standard-Webhooks
  `v1,<sig>` format). All clean — regression nets, no new defect.
- **R409 (fourteenth window, SCIM op-path case + property net)**: a
  hypothesis totality property over `_normalize_path` surfaced that the
  Group PATCH filtered member-remove regex `members[value eq "..."]`
  matched the path CASE-SENSITIVELY while the rest of the op grammar
  lowercases — a case-varying IdP's member removal silently no-op'd.
  Fixed: regex keywords case-insensitive (captured member id stays
  case-exact), misleading "lowercase the attribute" docstring corrected
  (case is preserved by design for the filter id). Pinned both as a
  property (totality) and an example (capital "Members" removes). SCIM
  suite 38/38.
- **R408 (fourteenth window, SSRF soundness properties)**: the egress
  validator had a TOTALITY property (never leaks a parser error over
  arbitrary URL text) but no SOUNDNESS property (never ADMITS a
  private/metadata target). Added hypothesis tests that generate the full
  IPv4 space + the canonical metadata/loopback/private literals and their
  IPv4-mapped-IPv6 encodings, cross-check against the authoritative
  _is_forbidden_ip classifier, and assert validate_egress_url REFUSES
  every forbidden one in production mode — a URL-parse-confusion bypass
  would fail here. Posture clean; this closes the "no-crash ≠ no-bypass"
  gap on the single most security-critical fabric parser.
- **R407 (thirteenth window, close)**: migration chain intg18→intg21 all
  reversible (4-hop drill), all 10 operational drills green, battery 377,
  parity clean. Window 13 total R394-R407: 2 production security fixes
  (R396 DNS-pin dispatcher, R401 rotation lock), 1 latent nightly-sweep
  aborter (R402), 2 index regressions the EXPLAIN drill caught as data
  grew (R393/R406 class, now intg20/intg21), 3 new fuzz phases reaching
  real SAML/LTI/OIDC surfaces, 2 new drills (RSS soak, HTTP idempotency),
  `make drills`. Head intg21a00021; not merged, no PR.
- **R406 (thirteenth window, connection-sweep index — drill pays off #2)**:
  the EXPLAIN drill flagged its SECOND real regression this window —
  intg_connections crossed 10k rows and the health sweep slice
  (status active/degraded ORDER BY updated_at LIMIT 100) started
  seq-scanning. Migration intg21a00021 adds partial index
  ix_intg_conn_sweep (updated_at WHERE status active/degraded), declared
  in the model for parity; drilled down/up; EXPLAIN flagged=0; battery 377. R393 + R406 are the same drill catching the same class twice as
  the data grew — exactly why it is checked in.
- **R405 (thirteenth window, final tally + flake kill)**: the global
  LIMIT-200 domain sweep could crowd a test's own pending rows out of the
  batch — the sweep test now isolates by deleting other pending rows
  first (test hygiene; the sweep itself is robust since R402), and the
  storm namespaces all resources per run (no more cross-run dup domains).
  Closing wave: 12/12 chunks = 10,787; battery 377; lifecycle 77/77;
  scale 37/37; storm 8/8; fuzz 399 req/seed zero-5xx envelope-clean (20+
  seeds this window, ~8,000 hostile requests); adversarial 178/0; walk
  65/65; web 766; all 10 drills green via `make drills`. Head
  intg20a00020; no merge/PR per standing rule.
- **R404 (thirteenth window, HTTP idempotency-race drill)**: the in-process
  DB test proved the import idempotency service; this proves the FULL ASGI
  stack under real socket concurrency — 12 simultaneous uploads with the
  same idempotency_key yield exactly ONE job id, zero 5xx (uq_intg_import_idem
  - the R111 savepoint recovery). Checked in as
    tests/drills/idempotency_drill.py and added to `make drills` (now 10).
- **R403 (thirteenth window, closing tally)**: full sweep after R394-R402:
  12/12 chunks = 10,787 backend tests; battery 377; lifecycle 77/77;
  scale 37/37; storm 8/8 (now exercises the R401 rotation race on a
  shared hook); fuzz 399 req/seed zero-5xx envelope-clean; adversarial
  178/0; walk 65/65; CI fabric specs 9/9; web 766 + tsc + eslint; all 9
  operational drills green via `make drills`; head intg20a00020. Two
  production fixes this window (R396 DNS-pin, R401 rotation lock) and one
  latent nightly-sweep aborter (R402), all pinned.
- **R402 (thirteenth window, domain-sweep session poisoning)**: a latent
  bug the storm cruft surfaced — when TWO orgs hold the same pending
  domain and both pass DNS in ONE sweep pass, the second verify hit
  uq_intg_domain_verified inside the savepoint; asyncpg marks the whole
  transaction failed, so the per-row commit raised PendingRollbackError
  and aborted the rest of the nightly sweep (every later domain left
  unprocessed). The savepoint-rollback-alone pattern does NOT contain a
  flush failure in async SQLAlchemy once the per-row commit model is in
  play. Fixed: pre-check the partial-unique winner before flipping to
  verified (the same guard claim()/verify() use), with an explicit
  session rollback + fresh-transaction failed-mark as the belt for the
  true concurrent race. Pinned; sso suite 41/41. (Also: storm runs leave
  global pending-domain cruft in the dev DB — the storm now seeds
  org-unique domains going forward would avoid that, but the real fix is
  the sweep being robust to duplicates, which it now is.)
- **R401 (thirteenth window, rotation row-lock)**: webhook secret
  rotation was an unlocked read-modify-write on (secret, secret_prev) —
  two concurrent rotations both read secret S, both set prev=S, and the
  loser's one-time reveal was silently dead. Rotations now serialize on
  a row lock (the R207 class, applied to the one remaining chained-prev
  structure in the fabric). 17 rotation tests green.
- **R400 (thirteenth window, discard-mode completion)**: the sync webhook
  test dispatch gets discard_body too, and discard mode now also skips
  the declared Content-Length screen — a receiver declaring a huge body
  is irrelevant when the body is never read; "accepted" is the only
  signal delivery cares about. Unit pin: discard returns status with
  EMPTY content against an over-cap body while normal mode still raises
  EgressBlockedError. Side effect: the webhook delivery test block
  dropped 38 s → 7 s (no more draining receiver bodies).
- **R399 (thirteenth window, `make drills`)**: one command runs the whole
  operational drill suite in sequence (redis/minio outage, crash,
  migration 4-hop, rate-limit engagement, slow-sink, backup/restore,
  EXPLAIN audit, RSS soak) and fails fast — first full run: ALL DRILLS
  OK in ~8 minutes. The ops doc's drill table is now executable.
- **R398 (thirteenth window, RSS soak drill)**: prior soaks proved
  latency stays flat; this one proves the PROCESS doesn't grow — 12
  consecutive storms (~2,400 mixed CRUD ops) against one uvicorn worker
  with RSS sampled per storm: flat at ~244 MB, ending LOWER at 230 MB
  (GC), p95 range 413-650 ms. Gate: final < 2x warm and < 1.5 GB.
  Checked in as tests/drills/soak_drill.py (takes N as argv).
- **R397 (thirteenth window, backchannel-logout fuzz)**: phase 9b mints a
  real ACTIVE OIDC connection and fires hostile logout_tokens (alg:none,
  HS256 confusion, garbage, 10 KB blobs) at /oidc/backchannel-logout —
  the last JWT-consuming surface that was only fuzzed at its lookup
  wall. Fuzzer now 399 req/seed; seeds 13020/13021 clean.
- **R396 (thirteenth window, legacy dispatcher gets the DNS pin)**: the
  legacy webhook dispatcher re-validated the URL per retry but still
  DIALED BY HOSTNAME — a rebind between validate and connect slipped the
  wall. It now sends through EgressClient (resolve → validate every IP →
  dial the pinned literal), with a new `discard_body` mode preserving the
  R171 never-read-the-receiver's-body property (close after the status
  line). Two spillover wins: (1) one shared SSLContext — httpx parsed the
  full certifi CA bundle (~2 MB) per AsyncClient, and delivery minted a
  client per attempt; built once at import now. (2) The egress port
  allowlist documented + pinned as PROD-only (egress_allow_private lifts
  it for local test sinks; scheme/userinfo walls hold in every mode) —
  the lifecycle's port-wall check moved to the mode-independent userinfo
  wall with the prod port wall pinned in unit tests. Webhook suite
  120/120, lifecycle 77/77, battery 374.
- **R395 (thirteenth window, hostile-JWT fuzz at a real LTI launch)**:
  phase 9 mints an LTI registration and a fresh single-use state via
  /lti/login per attempt, then fires alg:none, HS256-confusion,
  kid-traversal, non-JWT garbage and empty-segment tokens at /lti/launch.
  Probe results: alg walls hold (401), RS256 path's JWKS fetch dies
  cleanly in the egress guard (422 EGRESS_BLOCKED, never a hang), huge
  JWTs capped at 16 KB by schema. Fuzzer now 394 req/seed; seeds
  13010-13012 clean.
- **R394 (thirteenth window, structured-XML fuzz at a real SAML conn)**:
  the proto fuzz cases 404 at connection lookup BEFORE any XML parses —
  the hostile payloads never reached the parser. Phase 8 mints an ACTIVE
  SAML connection (throwaway self-signed cert) per fuzz run and fires
  XXE, billion-laughs, 4000-deep nesting, external-DTD SSRF, unsigned
  assertion and NUL XML at its ACS: all clean 401s in ≤20 ms (parser
  flags resolve_entities=False/no_network/dtd_validation=False + the
  signature wall hold; the 1024 KB form-field cap stops oversized
  payloads earlier). Fuzzer now 389 req/seed; seeds 13001-13003 clean.
  Lesson: a fuzz case that dies at the lookup wall proves nothing about
  the parser behind it — provision the real resource.
- **R393 (twelfth window, retention-sweep index — the drill pays off)**:
  the checked-in EXPLAIN drill flagged its first real regression the same
  day it landed: today's storms pushed intg_sync_runs past 10k rows and
  the nightly retention delete (terminal status + created_at < cutoff)
  started seq-scanning. Migration intg20a00020 adds the partial index
  ix_intg_runs_retention (created_at WHERE status terminal), declared in
  the model so the parity guard stays green; drilled down/up; EXPLAIN
  flagged=0; battery 374; sync suite 47/47. This is the compounding
  loop working: R387 checked the drill in, R393 is the drill catching
  drift hours later.
- **R392 (twelfth window, closing regression tally)**: full sweep after
  R370-R391: backend 12/12 chunks = 10,786 tests; fabric battery 374;
  lifecycle 77/77; scale smoke 37/37; storm 8/8 (p95=840 ms under
  parallel churn; soak p95 441 ms warm); fuzz 383 hostile requests/seed,
  zero 5xx, 4xx envelope-clean (seeds 9100/99999 + 15 earlier this
  window); adversarial 178/0; browser walk 65/65; CI fabric Playwright
  specs 9/9 (sweep 4 + a11y 5); web 766 tests + tsc + eslint + build;
  head intg19a00019 (4-hop drill walks intg16→19). All eight drills
  green at head. Hygiene: clean tree, no stray listeners, empty stash.
- **R391 (twelfth window, SCIM Groups filter)**: /Groups silently IGNORED
  the `filter` query param — Okta dedups groups with `displayName eq
"..."` before creating, so the ignored filter returned the whole
  directory and let the IdP duplicate or mis-match groups. Now supported:
  case-insensitive `displayName eq`, exact `externalId eq`; any other
  attribute is a loud 400 invalidFilter (reject beats silently-ignore for
  protocol params). Pinned (narrowing, miss, unknown-attr 400, unfiltered
  list unchanged); SCIM suite 37/37, battery 374.
- **R390 (twelfth window, deliveries Load-older page test)**: symmetric
  vitest coverage for the deliveries cursor UI (append, cursor consumed,
  button hides at the end). Web 766 tests. Render gotcha: delivery rows
  show event_type, not the raw id — match what the DOM paints.
- **R389 (twelfth window, 4xx envelope invariant in the fuzzer)**: the
  fuzzer graduated from "never a 5xx" to also asserting the DOCUMENTED
  error contract — an httpx response hook validates that every 4xx any
  /orgs/ JSON surface returns parses as `{error: {code, message}}`
  (SCIM surfaces speak the SCIM error schema, protocol surfaces return
  redirects/XML — out of scope). One hook covers all seven phases.
  Seeds 8001-8003 all envelope-clean. Also verified locally that the CI
  Playwright fabric specs pass together (sweep-integrations 9/9 + a11y
  5/5 in 32 s).
- **R388 (twelfth window, endurance block)**: 10-seed fuzz marathon
  (3,750 hostile requests, zero 5xx) + 5-seed storm (all 8/8, p95
  442-531 ms) + a 10-storm SOAK on one server process (~2,000 mixed CRUD
  ops, 30 orgs): p95 improved as the process warmed (892→441 ms), no
  pool-leak or drift signal. Plus one fuzz run against a DEV-mode server
  so the real rate limiter sat in the request path under hostile load:
  381 responses, zero 5xx (and zero 429 — the fuzzer's per-route rate
  stays under budget; limiter ENGAGEMENT is the R366 drill's job).
- **R387 (twelfth window, EXPLAIN drill in-repo)**: the R336 query-plan
  audit (EXPLAIN over ~26 fabric hot predicates on the 1M-row dev DB,
  flagging Seq Scans on >10k-row tables) moved into tests/drills/ with
  the other drills. Re-run at head post-intg18/19: flagged=0; the two
  domain probes had drifted to a stale table name (org_domains →
  intg_org_domains) — fixed in the checked-in copy.
- **R386 (twelfth window, mid-window full wave + all-drills pass)**: after
  R370-R385 the whole surface re-proved: backend 12/12 chunks = 10,785
  (one find: ruff B033 duplicate in AUDIT_ACTIONS — the registry's own
  lint); battery 373; lifecycle 77/77; scale 37/37; storm 8/8
  (p50=99 ms, p95=731 ms); fuzz 375 req/seed zero-5xx (fresh seeds
  424242, 90125); adversarial 178/0; walk 65/65; a11y spec 5/5; web 765 +
  tsc + eslint + build. ALL SEVEN drills re-run green at head:
  migration 4-hop now walks intg16→intg19, crash kill -9, redis
  fail-open, minio clean-fail, slow-sink 15 s cap, rate-limit
  engagement, backup/restore. Web security headers verified already
  complete (XFO DENY, CSP, HSTS, nosniff — no gap).
- **R384 (twelfth window, audit-lands proof)**: record_fabric_audit is
  best-effort (swallows every failure with a warning), so R377's 19 call
  sites could all be silent no-ops while every STRUCTURAL guard still
  passed. New DB test writes the break-glass action for a real fabric
  org and reads the row back from cp_audit_events — actor, target,
  payload and tenant scope intact. The three audit guards now compose:
  action literals registered (R147), every mutating route calls or is
  exempt (R377), and the write path actually lands a row (R384).
- **R383 (twelfth window, a11y into CI)**: the fabric WCAG gate now runs
  on every push — new sweep-a11y-integrations.spec.ts (axe-core 2.1 A/AA,
  serious/critical fail) covers all five pages as an authenticated admin
  and joined the CI Playwright run list. Unlike the RUN_A11Y-gated
  one-off audit, this is unconditional: axe-core became a real workspace
  devDependency in R372, so no network fetch or staging step. Local run:
  5/5 in 27 s. Spec gotcha: Playwright transpiles specs as CJS —
  `createRequire(import.meta.url)` makes the file silently unloadable
  ("No tests found"); plain `require.resolve` works.
- **R382 (twelfth window, Load-older page test)**: vitest coverage for the
  keyset UI — first page renders with meta.has_more, clicking Load older
  issues `events?before=<cursor>`, the older page APPENDS (page 1 still
  visible), and the button disappears when has_more goes false. Also
  verified the uniqueness races are already mechanized (domain claim org
  lock + savepoint + IntegrityError recovery; verify partial-unique 409;
  SCIM Bulk bounded at 100 ops/413) — no gap found there. Web 765 tests.
- **R381 (twelfth window, S3 round-trip export proof)**: every export
  content assertion ran through MemWriter — the real S3PartWriter seam
  (bucket bytes, key layout, content type) was never exercised. New DB
  test runs an export through S3PartWriter against the real MinIO,
  fetches the part back from the bucket, and asserts the BYTES IN THE
  BUCKET are allowlist-narrowed ({id,type,subject} only) and anonymized
  (raw subject absent). PII governance now proven at the storage
  boundary, not just the writer interface.
- **R380 (twelfth window, slow-sink drill)**: slowloris receiver drill —
  a sink that ACCEPTS the connection then stalls 60 s must not wedge
  delivery. Proven live: the synchronous /webhooks/{id}/test dispatch
  returns `{delivered: false, error: "ReadTimeout", latency_ms: 15028}`
  at exactly the EgressClient 15 s read cap (no hang, no 500), and a fast
  sink on the same port delivers in 6 ms immediately after. Checked in as
  tests/drills/slow_sink_drill.py. Drill detail: the egress port
  allowlist {80,443,8080,8443} applies even in private-egress test mode —
  sinks must sit on 8080.
- **R379 (twelfth window, deliveries Load-older + audit-cost check)**: the
  deliveries list gets the same keyset Load-older as events (filter-reset,
  in-flight guard). Storm re-run after the 19 new audit writes:
  p50=135 ms, p95=732 ms — no latency regression from auditing every
  config mutation.
- **R378 (twelfth window, SCIM meta conformance + before-param fuzz)**:
  SCIM User/Group `meta` now carries `created`/`lastModified` (RFC 7643
  §3.1 SHOULD — Okta/Entra conformance checkers flag absence). Gotcha
  re-confirmed as a CLASS: reading `updated_at` in a sync serializer
  after a flush triggers MissingGreenlet (onupdate column expired) — new
  `_iso_loaded()` reads the ORM instance's loaded state only. The R375
  `before` cursor joined the fuzzer's query-param phase (375 req/seed,
  zero 5xx) after a hostile manual probe (NUL, emoji, SQL, boundary
  ULIDs) came back clean. Battery 372, SCIM suite 36/36.
- **R377 (twelfth window, audit-trail coverage — 19 new sites)**: a route
  probe showed only 18 of 48 mutating fabric routes wrote the audit trail;
  uncovered included **break-glass** (disabling SSO enforcement — the
  single most audit-worthy switch in the fabric), connection
  update/delete/upgrade, domain claim/verify/delete, sso-connection
  delete, scim-token group-map update, export stream create/update/
  delete/run, LTI registration create/dynamic/delete, roster provision,
  sync run/cancel, identity-queue resolve, delivery replay. All 19 now
  call record_fabric_audit (payloads carry config shape, never secrets).
  The existing R147 registry guard immediately caught that unregistered
  actions are SILENT NO-OPS in record_audit — all 20 action literals
  registered in AUDIT_ACTIONS. New coverage guard: every mutating
  /integrations route must audit in-handler or sit on an explicit exempt
  list (ping/previews/LTI protocol surfaces), so a new mutating route
  fails the battery until it declares its audit posture. Battery 372.
- **R376 (twelfth window, Load-older UI)**: the events page consumes the
  R375 cursor — a "Load older events" button appends keyset pages (older
  state resets on filter/org change, in-flight guard, disabled state).
  tsc + eslint + 764 web tests + 65/65 walk green.
- **R375 (twelfth window, keyset pagination on events/deliveries)**: both
  admin lists were head-limited (newest 200, nothing older reachable).
  Added `before` keyset cursors — ULIDs are time-ordered, so `id <
before` IS the time cursor, served by the primary-key index, and pages
  stably under concurrent inserts (no offset skip/dup). Envelope gains
  `meta: {next_cursor, has_more}` (CursorListResponse; limit+1 fetch
  answers has_more without a count). Gotcha pinned: direct (non-HTTP)
  callers hit the truthy Query default — `before` is isinstance-guarded.
  DB pin walks 7 events in 3 pages with zero overlap/skip; lifecycle
  gains a live two-page wall (77/77).
- **R374 (twelfth window, route-contract guard)**: structural test over
  every MOUNTED fabric route (108 collected by recursive router unwrap —
  this FastAPI version nests _IncludedRouters, so naive app.routes
  iteration sees zero): every /integrations route must carry
  get_current_user in its dependant tree (protocol surfaces auth
  in-handler and are out of scope), every JSON route must declare a
  response_model (204 DELETEs and deliberate raw responses — errors.csv,
  template, payload — allowlisted), and the org-scoped router must keep
  its router-level rate limiter (router-level deps do NOT appear in
  route.dependant here, which also explains why a per-route rate-limit
  scan was an artifact — R366's live drill is the engagement proof).
  First run: posture already clean; the guard exists so the NEXT route
  added without auth fails in the battery, not in an audit.
- **R373 (twelfth window, backup/restore drill)**: backups nobody has
  restored are Schrödinger backups — drilled the real path: pg_dump -Fc
  of the live dev DB (766 MB, 1,266,752 rows in scope) inside the
  postgres container, pg_restore --exit-on-error into a scratch DB
  (102 s dump / 169 s restore), then asserted alembic_version ==
  intg19a00019, all 31 fabric-scope table counts byte-for-byte equal,
  and an R371-encrypted webhook secret identical post-restore. Scratch
  DB dropped, dump removed. Checked in as tests/drills/
  backup_restore_drill.py.
- **R372 (twelfth window, axe-core WCAG 2.1 A/AA audit)**: new
  `make e2e-intg-a11y` runs the full axe-core ruleset (wcag2a/aa +
  wcag21a/aa — the VPAT procurement baseline) over the five fabric pages
  plus the auth pages as a logged-in admin, failing on any
  serious/critical violation and printing moderate/minor as advisory.
  All five fabric pages came back CLEAN on first run; the one serious
  violation (color-contrast) was the base dashboard's org-role badge
  using bg-secondary without its paired secondary-foreground text color —
  fixed in both occurrences. 7/7 pages clean after; web 764 tests + tsc
  still green. Note: /register and /login audited while authenticated
  redirect to /dashboard, so those rows effectively audit the dashboard.
- **R371 (twelfth window, webhook secrets encrypted at rest + intg19)**:
  secrets-at-rest audit: connection credentials and LTI private keys were
  Fernet-encrypted, SCIM tokens hashed — but webhook SIGNING secrets sat
  as plaintext String(64); a DB dump handed an attacker every org's
  delivery-forging key. Now: `encrypt_secret` on create/rotate (the
  one-time reveal rides a transient `plaintext_secret` attribute, never
  persisted), `decrypt_secret_tolerant` on every signing path (legacy
  plaintext rows decrypt to themselves until their next rotation), and
  migration intg19a00019 widens the columns and encrypted all 8,627
  existing rows in place (idempotent via length guard; drilled down/up).
  Pinned: round-trip + legacy tolerance + build_delivery_headers signs
  with the revealed plaintext for both storage forms. Lifecycle 75/75
  (live create→deliver→HMAC-verify loop), battery 369, webhook suite
  120/120. Lesson: audit at-rest posture per secret CLASS — the mesh's
  newest secrets had the oldest storage.
- **R370 (twelfth window, multipart fuzz phase + csv field-limit 500)**:
  fuzz phase 7 covers the one surface phases 1-6 never touched — the
  multipart import upload, which parses inline at create_job: 18 hostile
  files (binary garbage, fake xlsx/zip magic, bad UTF-8, NULs, BOM,
  unclosed quotes, 5000 columns, formula injection, emoji headers) ×
  hostile form fields × hand-rolled malformed multipart envelopes
  (bad/missing boundary, no file part, truncated). Found: a single CSV
  cell beyond Python's 128KB csv field limit raised `_csv.Error` out of
  `parse_users_csv` → 500 on upload. Fixed: both the header-row pull
  (`reader.fieldnames`) and the row loop wrap csv.Error into a clean
  per-file `malformed_csv` error. Pinned in test_integrations_core.
  Fuzzer total now 359 requests/seed; seeds 7001-7004 zero-5xx. Lesson:
  every content-type boundary (JSON done, multipart was not) needs its
  own fuzz phase — inline-parse-at-upload makes the uploader the parser's
  error boundary.
- **R369 (eleventh window, fabric model/migration parity guard + intg18)**:
  new DB test scopes alembic autogenerate comparison to intg_* tables and
  asserts an EMPTY diff — fabric must never inherit the base repo's
  model/DDL drift habit (`alembic check` fails repo-wide on older epics).
  First run found 41 real items: 40 timestamp columns the models declare
  NOT NULL (Mapped[datetime] + server_default=now()) that the hand-written
  DDL left nullable — a raw write could insert NULLs the ORM can never
  produce — plus the model not declaring ix_intg_events_time (intg17).
  Fixed by migration intg18a00018 (defensive backfill + SET NOT NULL on
  all 40, reversible — down/up drilled) and index=True on
  IntegrationEvent.time. Parity test green; battery subset + lifecycle
  75/75 after. Lesson: hand-written migrations need a scoped autogenerate
  guard from day one — nullability is the silent drift axis.
- **R368 (eleventh window, closing regression wave)**: full sweep after
  the window's fixes (R353-R367): backend 12/12 chunks = 10,776 tests
  (one corpus-scan test updated to windowed matching after the R364
  format sweep); web 764/764 + tsc + eslint; fabric battery 368;
  lifecycle 75/75; scale smoke 37/37; fuzz zero-5xx (seed 43 + 2027/
  31337/99991/777 earlier, 330 hostile requests each); storm 8/8 with
  latency SLO (p50=146 ms, p95=665 ms); adversarial 178/0; browser walk
  65/65 in ~2 min (post-R363/R367); alembic head intg17a00017 (the
  repo-wide `alembic check` drift is pre-existing base-repo
  model/migration divergence in older epics' tables, not fabric).
  Hygiene: clean tree, zero stray listeners, zero backups, empty stash.
- **R367 (eleventh window, drills into the repo + system-proxy class)**:
  the five operational drills (redis/minio outage, kill -9 crash,
  4-hop migration, rate-limiter engagement) moved from throwaway job
  tooling into `apps/api/tests/drills/` with repo-relative paths and a
  README (what each breaks, what it asserts). Porting them surfaced a
  new environment class: the user's macOS SYSTEM proxy came on
  mid-session and urllib honors SystemConfiguration even with clean env
  vars — localhost requests 502'd through the proxy. All drills now
  install a direct (no-proxy) opener, the browser walk launches Chromium
  with --no-proxy-server, and the httpx suites were already safe
  (trust_env=False skips env; httpx never reads macOS system proxies).
  Lesson: "no proxy env vars" proves nothing on macOS — force direct
  handlers for loopback tooling.
- **R366 (eleventh window, rate-limiter engagement drill — two production
  fixes)**: every live suite runs APP_ENV=test where rate limiting is
  skipped, so the 429 path had never been exercised live. A dev-mode
  drill (burst a 10/60 route) found: (1) **stacked-budget halving** — the
  redis key was (method, route template, identity) only, so a route-level
  limiter inside the router-level one incremented the SAME sorted set
  twice per request; the 10/60 route tripped 429 at the 6th call. Key now
  embeds (limit, window). (2) **envelope drops exception headers** — the
  global HTTPException handler re-rendered into the error envelope
  without `exc.headers`, so 429s lost Retry-After/X-RateLimit-* and 401s
  lost WWW-Authenticate. Handler now passes them through. Drill after:
  exactly 10 allowed (transparency headers present), 11th = 429 with
  Retry-After: 60, sibling route unaffected (per-route bucket). Both
  pinned in test_core_unit.py. Lesson: a test-mode skip means the guarded
  path needs its own engagement drill — fail-open proofs are not
  engagement proofs.
- **R365 (eleventh window, storm latency SLO)**: the concurrency storm
  now records every request's wall time and asserts a latency SLO on top
  of zero-5xx: p50 < 1 s, p95 < 5 s under 20 workers of mixed CRUD on a
  loaded dev box. Measured: p50=125 ms, p95=740 ms, p99=1020 ms,
  max=1046 ms (n=195, seed 17). A p95 regression here is a lock-contention
  or N+1 smell even when nothing errors. R364: one-time ruff-format sweep
  (153 files) — `gh run list` showed zero Actions runs on the branch, so
  the `ruff format --check` CI gate added earlier had never actually
  executed and was unsatisfiable; battery 368/368 after the sweep.
- **R363 (eleventh window, walk de-flaked — cold-compile/networkidle class)**:
  the 65-check browser walk crept from ~3 min to ~11 min and started
  blowing runner budgets. Two independent causes: (1) cold next-dev
  compiles under load made first-visit gotos eat 20-30 s (fixed: runner
  pre-warms /register,/login,/dashboard,/orgs/new before the walk; all
  goto timeouts raised to 90 s as backstop); (2) `waitUntil: "networkidle"`
  blocks ~30 s per navigation against next-dev because HMR keeps a
  long-lived request open — 17 uniform 30 s gaps measured in the API log
  while no API call exceeded 5 s. Fixed: every goto/reload uses
  `waitUntil: "load"` + a 2.2 s settle sleep. Walk: 65/65 in 109 s.
  Lesson: networkidle is a dev-server trap; never diagnose walk slowness
  from the walk's own output — diff server-log timestamps for uniform gaps.
- **R362 (eleventh window, dependency-outage drills)**: stopped the real
  infra containers mid-traffic. REDIS down: 20 authed reads+writes all
  answered (metering/rate-limit fail-open held, zero 5xx), full function
  on restart. MINIO down: an export run lands as a CLEAN terminal
  `failed` row (202 envelope, no 500, nothing stuck), and the rerun after
  recovery succeeds — the cursor-only-advances-on-success rule means no
  data loss across the outage. Both drill scripts kept under the job
  tmp tooling.
- **R361 (eleventh window, crash-recovery drill)**: kill -9'd the API
  12 seconds into a 20-worker write storm, restarted, and asserted the
  healing invariants: zero import jobs stuck in committing/validating
  (the single-transaction commit design rolls the claim back with the
  work), no fresh orphan running runs/exports (the reaper owns older
  ones), clean restart, battery 368 and lifecycle green immediately
  after. R359/R360: query-param fuzz phase (330 hostile/seed) and the
  fuzz step wired into the CI fabric job.
- **R358 (eleventh window, fuzz phase 5 + fourth 500)**: SCIM PATCH
  path-filter bombs (unclosed brackets, emoji filters, 3KB expressions,
  2,000-op arrays, non-string paths) — found the window's FOURTH 500:
  op path=123 reached str.strip() in _normalize_path (both user and
  group PATCH). Guarded with a clean 400 invalidPath, unit-pinned, 290
  hostile requests per seed now zero-5xx across 3 seeds.
- **R356/R357 (eleventh window, fuzzer phases 3-4)**: hostile-HEADER
  phase (8KB bearer, junk JWT shapes, giant XFF) and the unauthenticated
  PROTOCOL surface (discovery with hostile emails, authorize/callback
  junk, ACS garbage b64 + oversized RelayState, SLO junk query, bcl
  junk/oversized tokens, lti login/launch junk) — 269 hostile requests
  per seed, zero 5xx across 4 more seeds. The tokenless surface holds.
- **R355 (eleventh window, response hardening + drills)**: live header
  audit found two gaps — authed JSON had NO Cache-Control (token-gated
  data cacheable by intermediaries/bfcache) and the Server header
  fingerprinted uvicorn. The security middleware now stamps
  `Cache-Control: no-store` on /api responses (route-set values win) and
  overrides Server; every runner/make target/CI uvicorn start gained
  `--no-server-header`. Pinned live in the lifecycle (rides CI). Also:
  4-hop migration drill (head -> intg13 -> head, every hop verified) on a
  scratch DB — clean.
- **R354 (eleventh window, concurrency storm)**: new live storm
  (`tests/e2e_storm_fabric.py`, `make e2e-intg-storm`) — 20 workers x 15
  rounds of interleaved admin CRUD in one org (connections/streams/
  profiles/tokens/domains/webhooks create-patch-delete, trigger+cancel).
  Asserts zero 5xx, no request past 20s (deadlock guard), bounded
  wall-clock, and terminal consistency (both caps respected, no orphan
  live runs). 4 seeds green — the R260-class locks hold at surface level
  under genuine interleaving.
- **R353 (eleventh window, FUZZER + 3 real finds)**: new bounded seeded
  live-HTTP fuzzer (`tests/e2e_fuzz_fabric.py`, `make e2e-intg-fuzz`) —
  hostile bodies (wrong JSON types, NULs, 4KB strings, deep nesting,
  junk path ids) across every fabric mutating route, asserting the one
  platform invariant: NEVER a 5xx. First run found THREE production
  defects: (1) /Bulk 500 — `BULK_REQUEST_SCHEMA not in schemas` with a
  float schemas (TypeError before validation); members=float on group
  PUT crashed the same way; both now clean 400s with container guards.
  (2) LOG AMPLIFICATION — one unhandled exception rendered a rich
  traceback WITH LOCALS, expanding the route table into ~550k lines /
  ~100MB of log per 500 (a disk-filling primitive); the console renderer
  now uses bounded plain tracebacks — the same change took the fuzz run
  from 128s (server busy RENDERING) to 2.9s. (3) two SCIM routes parsed
  the body OUTSIDE the _run wrapper, so _json_body's own ScimError
  escaped as a 500 — parse moved inside. 6 seeds x 250 = 1,500 hostile
  requests now pass with zero 5xx; fabric battery green.
- **R352 (tenth window, terminal-HEAD chunk proof)**: all 12 backend
  chunks re-run AT THE FINAL HEAD after the last test additions — 10,772
  items, zero failures; the closing evidence is a full pass of the exact
  shipped tree.
- **R351 (tenth window CLOSE — final tally)**: window 10 (single-chat
  foreground, T0 22:34) R319-R350, ~33 commits. FIXES: R319 IDN
  normalization split-brain (security/i18n), R330 last-owner deprovision,
  R331 last-designee under enforce, R334 lower(email) functional index
  (1M-row seq scans -> point lookups, intg16), R336 events time index
  (intg17), R337 import row cap, R344 MissingGreenlet 500 on connection
  PATCH (expired onupdate column), R320 fixture ordering. NEW EVIDENCE
  INFRA: 37-check scale smoke covering ALL FIVE pipelines at size
  (+tidy), lifecycle grown to 74 with live PATCH/Groups/break-glass/
  cancel/queue walls (R344 heuristic mechanized via OpenAPI diff), CI
  gains the fabric Playwright sweep + live-E2E job, fabric files
  format-clean for the CI gate, JWKS-floor + private_key_jwt conformance
  pins, make targets hardened against port-handoff races (R350).
  Terminal state: 12 chunks zero-fail (10,772), battery 366, web 764 +
  build, lifecycle 74/74, scale 37/37, adversarial 178/0, walk 65/65,
  migrations reversible at intg17. Branch pushed; NOT merged.
- **R350 (tenth window, DX)**: both self-hosting make targets clear
  :8443 before binding — back-to-back invocations no longer race the
  dying predecessor.
- **R349 (tenth window)**: identity-queue resolve walled live too (a
  pending row minted in-process; producing one over HTTP needs a real
  IdP's ambiguous assertion). Lifecycle 74/74.
- **R348 (tenth window, never-called-live closure)**: mechanized the
  R344 heuristic — diffed the fabric OpenAPI (method, path) table against
  what the four live scripts actually call, then walled the risky
  flush-then-serialize leftovers live: SCIM Groups full cycle
  (create/PATCH/GET/DELETE over real HTTP + scim content types),
  break-glass set/unset (the route returns 204), and sync-run cancel.
  Lifecycle 73/73. Remaining uncalled routes are either IdP-side
  endpoints that need a real IdP round-trip (ACS, OIDC callback, bcl,
  SLO — covered by their service-level signature suites), dynreg (needs
  a live platform), or other epics' surfaces.
- **R347 (tenth window, final regression record)**: terminal-HEAD
  verification — backend 12 chunks zero-fail (10,772 items), fabric
  battery 366, web 764 + tsc + eslint + production build, live lifecycle
  66/66, scale smoke 37/37 (all five pipelines at size), adversarial
  178/0, browser walk 65/65, migrations fresh-DB reversible at intg17.
- **R346 (R344 class closure)**: live PATCH walls added for the
  remaining update routes only ever exercised in-process — sync-profile
  schedule (round-trip) and webhook re-enable. Lifecycle 66/66; every
  fabric PATCH surface now has at least one live-HTTP exercise riding CI.
- **R345 (tenth window, lifecycle gains the PATCH wall)**: the live
  lifecycle now PATCHes a connection and asserts updated_at serializes
  (the exact R344 crash shape) — 63 checks, and the regression wall rides
  the CI e2e-integration-fabric job.
- **R344 (tenth window, 500-class fix — expired-column lazy refresh)**:
  the smoke's tidy PATCH was the FIRST live-HTTP connection update any
  suite ever made — and it 500'd with MissingGreenlet: the update flush
  expires the server-onupdate updated_at column, the response serializer
  reads it, and the implicit lazy refresh runs outside the greenlet.
  Create already refreshed; update now does too. Swept the sibling
  routers: connections was the only one serializing updated_at. Smoke
  37/37 (incl. the new tidy section that parks the active connection so
  the half-hourly health sweep stops pinging every past run's fake URL,
  R150 class). Fake-connector contract note: read() yields
  {"records": [...], "state": {...}}, not bare lists.
- **R343 (tenth window, provision-scale 7b)**: the 1,000 staged classes
  are then provisioned — 1,000 cohorts auto-created through the governed
  path within its bound. 35/35; the smoke's five pipelines all run at
  size end to end (stage AND apply for sync).
- **R342 (tenth window, sync-pull-scale section)**: section seven stages
  1,000 connector records through execute_run (profile + run minted via
  the API, a two-batch in-process fake registered for the pull) — staged
  count exact, run succeeded, bounded. The smoke now covers ALL FIVE
  fabric pipelines at size: SCIM directory, imports (users+roster), mesh
  fan-out, warehouse export, and sync pull. 33/33.
- **R341 (tenth window, export-scale section)**: section six exports the
  org's 200+ mesh events to object storage through the API run endpoint —
  succeeded, row_count verified, bounded. The smoke now exercises every
  fabric pipeline at size: directory (SCIM), import (users+roster), mesh
  fan-out, and export. 28/28.
- **R340 (tenth window, roster-scale section)**: the smoke's fifth
  section enrolls all 500 imported users into one cohort through the
  roster import (the add_member funnel with its capacity lock, 500 rows)
  — 25/25 within bounds.
- **R338 (tenth window, walk-harness scoping note)**: attempted an
  internal-LTI-issuer negative in the walk; it CANNOT prove the egress
  screen there — the walk's API runs EGRESS_ALLOW_PRIVATE=true for its
  local sinks, so the screen is off by design (the 409 the probe got was
  a prior run's identical literal, not a wall). The negative is
  deliberately omitted with an explanatory comment; the egress walls stay
  proven by the adversarial battery against a production-flagged server.
  Environment-vs-assertion scoping recorded as a walk-design rule.
- **R337 (tenth window, import row-count cap)**: the 50MB byte cap alone
  admits ~1M CSV rows — all parsed into memory and, on commit, a
  savepoint per row (the R329 smoke measured 175ms/row even BEFORE the
  index fix; a million-row hostile file is an hours-long request).
  MAX_IMPORT_ROWS=100,000 enforced in the format dispatcher as ONE
  file-level `row_limit` error for both CSV and JSON; MAX_ROW_ERRORS
  (10k) already bounded stored error rows. Pinned both formats + at-cap
  acceptance; cap-removed mutant KILLED.
- **R336 (tenth window, PERF — EXPLAIN audit + events time index)**:
  generalized R334 into a systematic EXPLAIN audit over ~26 fabric
  hot-path predicates against the million-row dev DB. One more real find:
  the retention sweep's global `time < cutoff` on intg_events (the
  fastest-growing fabric table — every mesh emit) sequential-scanned
  nightly, because the only time-bearing index leads with org_id.
  intg17a00017 adds ix_intg_events_time; plan flips to an index scan;
  fresh-DB reversibility re-verified at intg17. Everything else indexed
  clean (deliveries, staged, runs, links, members, users-lower, domains,
  import jobs/errors, export runs, subs).
- **R335 (tenth window, mid regression record)**: post R319-R334 (IDN
  split-brain, ordering fixture, fabric format-clean, CI sweep + live-E2E
  jobs, JWKS floor + private_key_jwt pins, 22-check scale smoke, last-
  owner/last-designee guards, lower(email) index + intg16) the whole
  stack re-verified foreground: 12 chunks zero-fail, fabric battery 365,
  web 764 + tsc + production build, live E2E 62/62, adversarial 178/0,
  walk 65/65, scale 22/22, migrations fresh-DB reversible at intg16.
- **R334 (tenth window, PERFORMANCE fix — lower(email) seq scan)**: the
  scale smoke's third section (500-row CSV import) blew its bound at
  87.7s (~175ms/row) and led straight to the real cause: every identity
  path compares `lower(users.email)` (SCIM create/filter dup-checks, JIT
  verified-email matching, import row dedup) but the only email index is
  the plain unique btree(email) — at the dev directory's 1,078,425 user
  rows each lookup was a parallel sequential scan. New migration
  intg16a00016 adds the functional index ix_users_email_lower; the plan
  flips to an index scan and the whole 22-check scale smoke passes every
  bound (commit back under its 60s ceiling). Fresh-DB zero->head and
  head-reversibility re-verified at intg16. This is the class the smoke
  exists for: invisible at unit-test row counts, catastrophic at
  directory scale.
- **R333/R332 (tenth window, guards + DX)**: doc-reference guard — every
  tests/*.py|mjs path the ADR/ops doc name must exist (a renamed suite
  can't leave docs pointing at nothing). The scale make target gained
  EGRESS_ALLOW_PRIVATE (its mesh section delivers to a local sink; the
  first run without it failed exactly as the screen should make it fail).
- **R331 (tenth window, R330 class — last-designee guard)**: the same
  last-X sweep found the symmetric hole on break-glass: the owner could
  retire the LAST designee while a connection still enforces SSO —
  silently deleting the escape hatch the enforce flip REQUIRED (§5.2).
  set_break_glass(enabled=False) now refuses (409 BREAK_GLASS_REQUIRED)
  when an active enforced connection exists and no other designee
  remains; pinned three ways (refused+flag intact; second designee frees
  the first; enforce-off frees the last); guard-removed mutant KILLED.
- **R330 (tenth window, SECURITY/availability fix — last-owner
  deprovision)**: the scale smoke found it the honest way — its own bulk
  deactivate archived the admin who minted the token, and every
  subsequent admin call 403'd. SCIM deactivate/DELETE could archive the
  LAST active OWNER (bricking the whole owner/admin-gated surface with
  every owner session revoked on top). _deprovision now refuses (409
  mutability) when the target is the only active owner; with a second
  owner present it proceeds. Pinned both ways (PATCH active=false and
  DELETE refuse; membership untouched; allowed after a second owner);
  guard-removed mutant KILLED. The smoke's mesh section also landed: 200
  events -> 2 subscriptions -> 400 live deliveries to a local sink, all
  succeeded within bounds, stats endpoint agreeing. 17/17.
- **R329 (tenth window, scale smoke)**: first realistic-size run —
  `tests/e2e_scale_smoke.py` (+ `make e2e-intg-scale`) creates 300 SCIM
  users 10-way concurrent over live HTTP, pages the whole directory
  through the SQL-side pagination, point-looks-up one user by eq filter,
  and bulk-deactivates 50 — each under a generous wall-clock bound (the
  R218 O(N)-regression tripwire at sizes the unit suites never reach).
  11/11 green on first run (create 300 well under 60s, paging under 15s,
  filter under 2s, bulk under 20s). Soak this window: fabric battery x2
  and races x3 back-to-back, zero flakes.
- **R327 (tenth window, walk — LTI registration journey)**: the LTI
  Register-LMS form was the last create surface the walk never drove —
  now filled end-to-end (issuer/client/URLs/deployment ids -> row
  listed). 65/65 PASS; every fabric admin create form is browser-proven.
- **R326 (tenth window, private_key_jwt conformance pin)**: the
  client_credentials grant's client_assertion had no shape test — a
  drifted claim (iss/sub/aud/jti/exp) or a key not in our advertised
  JWKS fails every AGS/NRPS call at real LMSes with opaque 401s. Pinned:
  form fields (grant_type/assertion_type/scope), RS256 + kid header, the
  assertion VERIFIES against our own /lti/jwks (exactly what the platform
  does), iss=sub=client_id, aud=token URL, 16+-hex jti, exp-iat <= 300s.
- **R325 (tenth window, JWKS refetch-floor pin)**: coverage mapping
  (services 81-100%, routers covered by the live suites) pointed at the
  JWKS cache paths — the kid-miss 30s refetch floor (an attacker spraying
  random kids must not stampede our egress at the IdP) had NO direct
  test. Pinned 4 ways on a monotonic-clock fake (no-cache fetch, cache
  hit, in-floor miss returns stale with ZERO fetches, post-floor miss
  refetches once); floor-removed mutant KILLED.
- **R324 (tenth window, fabric live E2E in CI)**: new CI job
  `e2e-integration-fabric` (postgres/redis/minio services + alembic head
  - `make e2e-intg`) runs the 62-check live-HTTP lifecycle on every PR —
    it existed only as a local marathon ritual before.
- **R323 (tenth window, fabric pages enter CI)**: CI's Playwright job
  never visited the five fabric pages — a crashed page component or
  route rename would ship invisibly. New `e2e/sweep-integrations.spec.ts`
  (4 serial tests on the repo's own helpers: hub + connection create,
  identity domain-claim TXT + SCIM mint shown-once-gone-on-reload, events
  catalog + subscription secret, sync/data + stream create) added to the
  CI run list; 4/4 locally against live servers. Writing it exposed a
  stale assertion in the local walk (SCIM prefix is osks_scim_, not
  oskst_ — the old check passed via its OR-arm); fixed, walk 63/63.
- **R322 (tenth window, CI format-gate: fabric scope cleaned)**: CI's
  lint-backend job runs `ruff format --check .` — the R318 finding is not
  just a local make-target: a PR cannot pass CI with unformatted files.
  Of the 196 repo-wide, the fabric owns 51 (services/api/tests/contract
  guards) — all reformatted (semantics-preserving; ruff check and the
  360-test fabric battery stay green). The remaining ~145 belong to the
  unmerged upstream stack (talent/ecosystem/experiments branches) and are
  those PRs' concern.
- **R321 (tenth window, IDN-helper totality)**: hypothesis property over
  normalized_email_domain — arbitrary text folds to a lowercase domain or
  "", never raises (it sits on the login path; a hostile address must not
  500 the gate). 300 examples hold.
- **R320 (tenth window, ordering-hazard fix)**: a deterministic
  cross-file hazard surfaced while verifying R319 — test_auth.py's
  client-fixture tests leave pooled connections bound to a closed event
  loop, and saml_db's fixture only disposed AFTER the session, so the
  FIRST saml test crashed ("Event loop is closed") under auth->saml
  ordering. The fixture now disposes BEFORE minting the session too
  (lesson 4 completed: after-dispose protects the NEXT file, only a
  before-dispose protects THIS one).
- **R319 (tenth window, fix — IDN normalization split-brain)**: the claim
  path stores IDN domains as IDNA/UTS46 punycode (R83[M3]), but all three
  email-domain comparison sites (SSO discovery, the enforce gate, JIT
  email matching) derived the domain with a bare .lower() — an IDN
  tenant's unicode-address users silently fell out of discovery,
  enforcement and matching. New `normalized_email_domain` helper folds
  emails to the same canonical form (tolerant: unparseable -> no-match),
  wired at all three sites. End-to-end IDN pin (claim 'школа-*.рф' ->
  xn--, discovery routes, gate fires, identity matches); both bare-lower
  regressions revert-probed KILLED.
- **R317 (ninth window, terminal-HEAD chunk proof)**: after the last
  production edits (R311/R313), all 12 backend chunks were re-run AT THE
  TERMINAL HEAD — 10,765 items, zero failures — so the closing evidence
  is not "mid-window chunks + later diffs" but a full pass of the exact
  shipped tree.
- **R318 (ninth window, lint-gate audit)**: `make lint` (pnpm lint) is
  RED repo-wide on a format check — 196 files across every epic "would be
  reformatted" (fabric: 39 of ~53; the base epics carry the bulk). This
  predates issue #43: the per-window quality gate throughout has been
  `uv run ruff check` (green, repo-clean) + ESLint (green). A 196-file
  mechanical `ruff format` is a cross-epic churn decision (R189
  precedent) and a terrible end-of-window diff — documented for a
  dedicated formatting commit on the base branch instead.
- **R316 (ninth window CLOSE — final tally)**: window 9 (single-chat
  foreground, T0 17:30) R277-R315, ~38 commits. SECURITY/behavior fixes:
  R277 group_map foreign-cohort wall, R296 production build (never-run
  gate), R303 legacy dispatch proxy-env, R306/R308 terminal-claim races
  (cancel vs worker finish; queue double-adjudication), R311 90-day
  break-glass freshness (unimplemented ADR commitment), R313 break-glass
  IP+UA, R279 UI staleness, R280 retention, R309 alert edge-trigger.
  NEW INFRASTRUCTURE: 63-check Playwright fabric journey (creates,
  negatives, shown-once hygiene, outsider lockout, error report, 390px,
  a11y) + runner; web->API path+method contract guards; sweep source-scan;
  ops-caps doc guard; make targets (test-intg/e2e-intg/e2e-intg-browser).
  Probes: ~35 more mutants, survivors pinned (R278 trigger gates, R294/
  R295 update twins, R301/R302 client flags, R309, bulk failOnErrors-era
  carryovers) or documented equivalent. ADR-commitment sweep closed §5.2/
  §6 gaps (implemented, deferred-with-controls, or text aligned).
  Terminal state: backend 12 chunks zero-fail, fabric 358, auth 37, web
  764 + tsc + eslint + production build, E2E 62/62, adversarial 178/0,
  walk 63/63, ruff repo-clean. Branch pushed; NOT merged.
- **R314 (ninth window, ADR-reality alignment)**: the §6 credential
  advisory-lock clause described a refresh-token rotation flow that was
  never built — shipped connectors mint fresh client_credentials per run
  or use static api_keys, so there is no refresh race to lock; the
  invariant is held by the one-live-run index + the queued->running
  claim. Annotated the design text with the implementation reality
  instead of adding a lock with nothing to protect. Commitment sweep
  otherwise verified: tombstone-never-delete (R209), uniform-404 (R276),
  JIT never-above-instructor (R88 gates + R294 update twin), secrets
  never echoed (schema-level + walk R298), SCIM cross-org untouchable
  (R277), iss/state session-stored (pinned).
- **R313 (ninth window, fix — ADR commitment sweep continued)**: §5.2
  also promises the break-glass audit row carries "IP + UA" — the emit
  only carried user_id. login() already receives ip_address/device_info;
  threaded them through the gate into the event payload (UA capped at
  300 chars). Pinned. The third §5.2 clause ("WebAuthn-or-TOTP required")
  is documented as an explicit deferral in §19 (R312): the platform has
  no MFA infrastructure (Gap #181), compensating controls listed.
- **R311 (ninth window, fix — ADR commitment never implemented)**:
  §5.2's S1.3 runbook rule ("the rotation endpoint refuses 409
  BREAK_GLASS_UNVERIFIED if no break-glass login succeeded in the last 90
  days and enforce_sso is on") existed only in a docstring aside — the
  check was never written. Implemented on the manual refresh-metadata
  endpoint (keyed on the org.breakglass.login mesh events auth.py already
  emits): fires only when enforce_sso is on AND the cert set actually
  changes; the automated daily sweep stays exempt (zero-touch rotation
  must not wedge on an unused hatch) and a no-change refresh passes.
  Pinned 4 ways; revert-probed KILLED. Hunting heuristic: grep ADR
  MUST/refuses clauses and docstring asides for commitments with no
  grep-able implementation.
- **R310 (ninth window, shared-DB assertion hardening)**: R308's
  committed race rows tripped a latent time bomb — an old test asserted
  the reason of the LAST row of a GLOBAL unordered IdentityMatchQueue
  select (lesson 8/24 shape). Fixed the assertion to key on its own org,
  and the race test now tidies its committed row. Cert-expiry daily dedup
  probe KILLED. Fabric battery 356 green.
- **R309 (ninth window, alert edge-trigger pin)**: the unhealthy-alert
  edge condition (`status != before`) survived mutation — the existing
  transition test rode the auth->ERROR path, and parked connections leave
  the sweep set, making the mutant equivalent there. The spam surface is
  DEGRADED (still swept every 30 min): pinned with a timeout-degraded
  connection swept thrice more -> exactly ONE unhealthy event ever.
  Re-probed KILLED. Probe lesson: when a guard survives, ask which STATE
  keeps the entity inside the loop — that's the path the pin must ride.
- **R308 (ninth window, fix — queue-adjudication race)**: R306's class
  swept across terminal-state writers found one more check-then-set:
  resolve_queue_item read `status == "pending"` then wrote the terminal
  state — two admins adjudicating the same item concurrently could both
  pass (link+reject mix, or double link). Now an atomic
  pending->resolved claim (UPDATE ... WHERE status='pending' RETURNING)
  taken BEFORE the link work, so a failed link rolls the claim back with
  it. Race-pinned: two gather'd sessions, exactly one winner, loser 409.
  Swept the rest of the class: export runs (no cancel API), deliveries/
  imports (already claim-based), reaper (conditioned) — closed.
- **R307 (ninth window, final regression record)**: full foreground
  verification at window end — backend 12 chunks zero-fail (10,761 test
  items), fabric battery 354 (make test-intg), web 764 + tsc + eslint +
  PRODUCTION BUILD, live E2E 62/62, adversarial 178/0, browser journey
  63/63, migration chain fresh-DB zero-to-head + head-reversible.
- **R306 (ninth window, fix — zombie terminal overwrite)**: `_finish`
  set run.status unconditionally — an operator CANCELLING a running run
  mid-execution would get it flipped back to "succeeded" by the oblivious
  worker, complete with a bogus sync.completed event. The terminal
  transition is now an atomic claim (UPDATE ... WHERE status IN
  queued/running): if the cancel won, the worker's finish is a no-op and
  no event fires. Pinned both directions (cancelled stays cancelled with
  zero completion events; a running run still finishes normally);
  revert-probed KILLED.
- **R305 (ninth window, error-report journey)**: the walk uploads a CSV
  with an invalid row and asserts the operator-facing failure path: the
  dry-run surfaces a nonzero error count and the "Download error report"
  button appears. 63/63 PASS. (Walk-harness lesson: a journey that
  navigates away must re-navigate before the next section — a missing
  element inside an un-checked `if` silently skips the whole section;
  presence now asserted.)
- **R304 (ninth window, probe ledger)**: LTI launch-state single-use and
  expiry filters KILLED (R256's class, LTI edition); credential kind and
  value-shape validations KILLED; webhook-update unknown-event KILLED.
  Audited clean: login_initiation (target_link_uri unused; redirect goes
  only to the registration's egress-screened auth_login_url; login_hint
  urlencoded), all four repo AsyncClient constructions now carry
  trust_env=False (fabric, legacy webhook R303, ecosystem sync, workflow
  adapters), delivery timeouts bounded, fabric battery 353 green.
- **R303 (ninth window, SECURITY fix — legacy dispatch client flags)**:
  the R302 sweep found a SECOND outbound client: the legacy webhook
  dispatcher built a bare `httpx.AsyncClient(timeout=10.0)` — httpx
  defaults trust_env=True, so HTTP(S)_PROXY env vars would reroute every
  legacy delivery through an attacker-influenced proxy (redirects were
  safe by default but are now explicit). Fixed + pinned with the same
  **init**-spy test; revert-probed KILLED. Heuristic: grep EVERY
  `AsyncClient(` construction, not just the blessed wrapper.
- **R302 (ninth window, proxy-env pin)**: trust_env=False was the second
  unpinned hardening flag on the same constructor — with trust_env=True,
  an HTTP(S)_PROXY environment variable would silently reroute ALL pinned
  egress through an attacker-influenced proxy. Pinned at construction via
  an **init** spy (behavioral proxy routing is invisible under a patched
  transport); re-probed KILLED.
- **R301 (ninth window, redirect-SSRF pin)**: `follow_redirects=False`
  on the EgressClient had NO test — flipping it survives the whole core
  suite, yet following would fetch an attacker-chosen Location (cloud
  metadata IP) from inside our network, bypassing the URL screen
  entirely. Pinned at the TRANSPORT layer (httpx's redirect loop lives
  inside AsyncClient.send, so a send-level fake masks the flag): one hop,
  302 returned as-is, Location never fetched. Re-probed KILLED. Also
  audited clean this pass: delivery timeouts (connect/read/write/pool all
  bounded), secrets never logged, list endpoints bounded.
- **R300 (ninth window, outsider-lockout journey)**: the walk registers a
  SECOND user in a fresh browser context and drives them straight at org
  A's fabric URLs — neither the hub nor the identity page may leak any of
  org A's data (connection names, verification tokens, token names) to a
  non-member. 60/60 PASS. The browser walk now covers: happy paths for
  every create surface, negative UX, shown-once secret hygiene,
  cross-user lockout, mobile viewport, and form a11y.
- **R299 (ninth window, shown-once-really-once)**: the walk now reloads
  after minting the SCIM token and after creating the subscription, and
  asserts neither secret survives the refresh (shown-once lives in
  component state, never in a refetchable query). 58/58 PASS.
- **R298 (ninth window, browser walk — SSO create + secret hygiene)**:
  the walk now drives the OIDC SSO form (issuer + client id + secret ->
  Add OIDC) and asserts the listed row carries NO echo of the client
  secret anywhere in the rendered page (write-only secret, UI edition).
  56/56 PASS. Also: uv lockfile verified consistent; pnpm audit
  unavailable on the configured mirror registry (no audit endpoint) —
  noted, not actionable here.
- **R297 (ninth window, alembic-check audit)**: ran `alembic check` for
  model/migration drift (another never-run production gate). Findings:
  repo-wide, long-standing cosmetic drift — hand-written migrations omit
  explicit NOT NULL on TimestampMixin's created_at/updated_at (every
  epic's tables, user_points to webhook_subscriptions), plus a handful of
  base-epic FK ondelete/index declarations. The fabric's intg_* tables
  show ONLY the timestamp-mixin class, nothing structural; zero-to-head on
  a fresh DB remains verified working (R269). Normalizing the convention
  is a repo-wide, cross-epic migration change — documented here, not
  changed under issue #43 (R189 precedent).
- **R296 (ninth window, PRODUCTION-BUILD fix)**: `pnpm --filter web
build` had never been run in the marathons — and it FAILED: the
  experiments promotions page exported a test-only helper
  (`promotionsRefetchInterval`), which Next.js rejects as an unknown page
  export at BUILD time while dev and vitest both let it slide. Minimal
  cross-epic fix (no behavior change): moved the helper to the
  experiments lib module; page and test import from there. Build now
  compiles; web 764 + tsc green. Lesson: add `next build` to the
  regression cadence — dev-mode green does not imply deployable.
- **R295 (ninth window, R294 class — update-twin sweep)**: swept every
  fabric update twin. Webhook PATCH URL screen and the enforce/break-glass
  arm were covered; TWO more unpinned twins found and pinned — mapping
  update_document re-validates the document (and the version pin does NOT
  bump on a refused update) and sync-profile update re-validates
  field_policy. 3/3 re-probed KILLED. The update-twin class is now swept
  fabric-wide (sso_admin R294, warehouse batch-23, sync schedule batch-38,
  webhook/mapping/field_policy here).
- **R294 (ninth window, UPDATE-path validation pins)**: the create path's
  validations were all pinned, their UPDATE twins were not — three
  survivors on SsoAdminService.update (bogus status, admin default_role
  past the JIT mint ceiling, internal oidc_issuer past the egress screen)
  pinned in `test_sso_update_validations` (all refused, row unchanged);
  re-probed 4/4 KILLED (enforce-without-break-glass was already covered).
  Heuristic recorded: for every validated CREATE field, check the UPDATE
  path re-validates it — update twins rot unseen.
- **R293 (ninth window, mid-window regression record)**: after R277-R292
  (1 security fix, retention, 2 UI staleness fixes + placeholder bug, the
  53-check browser walk, 2 contract guards, sweep source-scan, ops-doc
  guard, DX targets, unicode pin) the whole stack re-verified foreground:
  12 backend chunks zero-fail, fabric battery 347 (make test-intg), web
  764 + tsc + eslint, live E2E 62/62, adversarial 178/0.
- **R292 (ninth window, unicode round-trip pin)**: CJK+emoji display
  names survive SCIM create/get, and the 100-char display-name cap cuts
  CHARACTERS not bytes (a 120-char CJK name truncates to exactly 100
  valid chars — a byte-slice would shear a multibyte sequence).
- **R291 (ninth window, DX targets)**: Makefile gained `make test-intg`
  (the 19-file fabric battery incl. both contract guards — 347 tests),
  `make e2e-intg` (self-hosting live-HTTP lifecycle on :8443, same idiom
  as e2e-exp) and `make e2e-intg-browser` (the Playwright journey).
  Verified: test-intg 347 green, e2e-intg 62/62.
- **R290 (ninth window, ops-doc caps drift guard)**: new
  `tests/test_ops_doc_contract.py` parses the operator caps table out of
  docs/ops and compares every row against the code constants — a cap
  change that skips the doc now fails CI (R231 drift class, docs
  edition).
- **R289 (ninth window, sweep-registry source scan)**: the sweep-cron
  guard's hand-maintained name list was itself the drift shape it guards
  against (sweep_import_files was already missing from it, though wired).
  Backed it with a source scan: every `async def sweep_*` under
  app/integrations must be referenced by the worker module — a brand-new
  sweep can no longer ship undriven. Detection proven by injecting a fake
  sweep (test fails and names it).
- **R288 (ninth window, method-level contract guard)**: second contract
  test matches every explicit-method page call (POST/PATCH/DELETE, ~30
  calls) against the operations the route actually serves — a page
  sending PATCH where the API serves PUT now breaks CI. Detection proven
  on domains/{id}/verify (POST->PATCH mutation fails the test and names
  the call); first probe target was a false negative because
  scim-tokens/{id} legitimately serves PATCH — the probe must mutate onto
  a method the route does NOT serve.
- **R287 (ninth window, cross-layer contract drift guard)**: new
  `tests/test_web_api_contract.py` extracts every template-literal API
  call from the five fabric pages (expanding the shared `base` prefix,
  dropping query strings and unclosed nested-ternary tails), and matches
  each against the resolved OpenAPI route table — a renamed or removed
  endpoint now breaks CI instead of 404ing an admin (the R63-R71
  login-journey class, mechanized). ~45 calls matched; detection proven
  by renaming a call in the page source (test fails, names the path).
  FastAPI note: `app.routes` now holds lazy `_IncludedRouter` entries —
  `app.openapi()["paths"]` is the authoritative resolved table.
- **R286 (ninth window, browser walk — a11y gate)**: section 9 audits
  every input/select/textarea on the five pages for an accessible name
  (aria-label, label[for], or wrapping label) — all clean. 53/53 PASS.
- **R285 (ninth window, browser walk — mobile viewport)**: section 8
  re-walks all five fabric pages at 390px asserting render + zero
  page-level horizontal overflow (tables scroll inside their own
  containers, the page itself never does). 48/48 PASS.
- **R284 (ninth window, browser walk — negative journeys)**: the walk now
  provokes rejections and asserts the UX: a freemail domain claim shows a
  visible "public email" error and the form stays interactive, and a
  plain-http webhook URL shows a visible egress error. The console gate
  exempts the browser's echo of these INTENTIONAL 4xx resource logs while
  still failing on any JS exception or React warning. 38/38 PASS.
- **R283 (ninth window, browser walk — create journeys)**: the walk now
  also drives the hub's New-connection form (generic_rest + base URL ->
  row listed with the write-only credential affordance) and the data
  page's export-stream form (name -> row listed). 35/35 PASS. Every
  fabric admin CREATE surface is now exercised in a real browser:
  connection, domain claim, SCIM token, webhook subscription, export
  stream, import job.
- **R282 (ninth window, browser walk — import journey)**: extended the
  walk with the full Part-K admin journey IN the browser: synthesize a
  users CSV, attach via the real file input, Upload & preview (dry-run
  stats render), Commit (job row flips to committed), then the imported
  member is visible on the org Members page. 30/30 PASS — the whole
  upload->preview->commit->membership chain now has browser-level proof,
  not just API-level.
- **R281 (ninth window, fabric BROWSER E2E + walk-caught UI bug)**: built
  `tests/browser_e2e_integrations.mjs` — a Playwright walk of the whole
  fabric admin journey (register -> org -> hub catalog+health -> identity:
  claim domain with visible TXT token + mint SCIM token with shown-once
  secret -> events: datalist catalog + create subscription with shown-once
  signing secret + row listed -> sync -> data: template buttons), with a
  strict console-hygiene gate (pre-auth 401 dance and one documented
  upstream layout nit exempted) and 4xx/5xx response tracing. 24/24 PASS.
  The walk immediately caught a real UI bug: the subscription form's
  placeholder recommended `project.approved`, which the API REJECTS (legal
  values are the legacy list or com.openskill.* mesh names) — an admin
  following the placeholder got a 422. Placeholder fixed to valid
  examples. Driver: `run_browser_e2e.py` boots api+web as process groups
  (killpg both; ports cleared first). Lesson 13 reaffirmed: the browser
  walk found in minutes what 338 fabric tests could not see.
- **R280 (ninth window, unbounded-growth round 3)**: table-by-table
  retention audit found two tables the nightly sweep missed — ExportRun
  (hourly streams mint ~720 bookkeeping rows per month EACH; manifests
  live in the bucket) and IdentityMatchQueue (resolved items are audit
  crumbs that accumulated forever). Both added to sweep_retention with
  the same batched-drain pattern: terminal export runs age out at 90d,
  resolved queue items at 180d; running runs and PENDING queue items
  never age out. Pinned (old-terminal gone / live+pending kept) and all
  three retention mutants KILLED.
- **R279 (ninth window, R229 class — UI staleness sweep round 2)**:
  re-ran the queryKey-vs-invalidation map over every fabric page. Two
  co-rendered queries were never invalidated: the hub page's health strip
  (`intg-health`) went stale after ping/create/delete/upgrade mutations
  (the strip kept old status counts while the table updated), and the
  events page's per-subscription stats (`intg-sub-stats`) went stale
  after replay/bulk-replay/delete. Both now invalidated alongside the
  primary keys; web 764 + tsc + eslint green.
- **R278 (ninth window, state-machine pins)**: the MANUAL trigger's own
  gates had no tests (the scheduler-side negatives were pinned in R243):
  triggering a disabled profile or a profile on a disabled connection must
  409, and cancel refuses an already-finished run (terminal status
  sticks). Pinned in `test_trigger_and_cancel_state_machine_guards`; both
  gate mutants re-probed KILLED.
- **R277 (ninth window, SECURITY fix — group_map foreign-cohort wall)**:
  extended the R276 heuristic from "is this id org-gated at READ" to "is
  this STORED id org-validated at WRITE and org-scoped at EFFECT". The
  SCIM group_map accepted ANY string as a cohort id: the join path was
  safe (CohortService.add_member checks org), but the group-LEAVE path
  deleted CohortMember keyed only on (cohort_id, user_id) — a foreign
  cohort id in group_map could unenroll a cross-org user from ANOTHER
  org's cohort. Fixed both layers: the delete now joins Cohort and
  requires org_id match, and create/update_group_map validate every
  cohort-mapped id belongs to the org (422 SCIM_GROUP_MAP_INVALID).
  Pinned with `test_group_map_foreign_cohort_walls` (validation at both
  write sites + smuggled-id leave leaves the foreign membership intact);
  both fixes revert-probed KILLED.
- **R276 (eighth window, org-gate completeness sweep — 6 IDOR pins)**:
  exhaustive probe of EVERY `org_id !=` gate in the fabric (11 sites, each
  occurrence by index). Five were already killed (subscription, import
  job, identity link, mapping get, export stream). SIX survived and are
  now pinned: the identity match-queue resolve gate (org B resolving org
  A's pending item), BOTH ScimTokenService gates (update_group_map and
  revoke — org B revoking org A's provisioning token), the sync-profile
  get gate, and the mapping-attachment gates on profile CREATE and UPDATE
  (a mapping id acting as a cross-org capability). Pinned in three tests
  (uniform 404, state untouched); all six re-probed KILLED. The org-gate
  class is now exhaustively probed fabric-wide.
- **R275 (eighth window CLOSE — final tally)**: window 8 (single-chat
  foreground, T0 12:26) R250-R274: 4 SECURITY fixes (R250 conflict IDOR,
  R251/R252/R253 issuer/entityID/origin mix-up trilogy, R260/R261 cap
  TOCTOU races, R272 SAML authorize open redirect), sprawl caps
  (R262/R263), 16 survivor-pin tests across SAML request-id, domain IDOR,
  mapping field cap, SLO/metadata DTD, bulk failOnErrors, push gates,
  sync-profile IDOR walls, SCIM PATCH envelopes; ~75 mutants probed with
  the hardened harness (path-existence assert + tail print + per-
  occurrence twin probing); layered-defense equivalents documented
  (bcl jti/alg, SLO unsigned/sigalg, router import cap). Final state:
  backend full suite 12 chunks zero-fail, fabric 338, web 764 + tsc +
  eslint, live E2E 62/62 twice, adversarial 178/0 twice, migration chain
  fresh-DB verified reversible. Branch pushed; NOT merged (one task = one
  PR awaits explicit instruction).
- **R274 (eighth window, twin-guard sweep round 2 — 3 pins)**: remaining
  duplicated-guard occurrences probed per-index. Profile-UPDATE schedule
  and mapping-create model guards KILLED. THREE survived and are pinned:
  SCIM user-PATCH and group-PATCH `Operations` envelope validation
  (missing/non-list/empty -> clean 400, never an iteration crash) and the
  metadata-refresh DOCTYPE screen (a DTD'd metadata document refused
  outright, same class as the R265 SLO pin). All re-probed KILLED.
- **R273 (eighth window, twin-guard sweep — 2 IDOR pins)**: generalized
  R272's lesson into a fabric-wide sweep of DUPLICATED guard lines (same
  `if` text in 2+ places), probing each occurrence by index. 8 org-gate
  occurrences probed: connections.get, sso_admin.get, both events-api
  delivery gates, the events-service replay gate and the engine's profile
  gate were KILLED; TWO survived — a sync profile could be CREATED against
  another org's connection (the connection id acting as a cross-org
  capability), and the profile DELETE route's org check had no test (org B
  deleting org A's profile). Both pinned in
  `test_sync_profile_cross_org_walls` (uniform 404, profile untouched);
  re-probed KILLED. Sweep heuristic recorded: duplicated guard text means
  the TEST corpus usually covers one twin — probe every occurrence.
- **R272 (eighth window, SAML authorize open-redirect pin)**: batch 36
  probed the twin return_to screens on the authorize routes. The OIDC
  occurrence was KILLED; the SAML occurrence (identical line, first in
  file) had NO test — a crafted /saml/authorize?return_to=https://evil
  link would mint state carrying the absolute URL and turn the post-IdP
  landing into an open redirect. Pinned at the ROUTE level (absolute and
  scheme-relative dropped -> state.redirect_to NULL; relative path
  preserved); re-probed KILLED. Probe-harness note: twin-occurrence
  anchors must be probed per-occurrence by index, not replace(...,1).
- **R271 (eighth window, import-cap layering)**: batch 34 probed the
  upload size cap. The router-side check is a documented layered
  equivalent (it bounds MEMORY by reading at most MAX+1 bytes before the
  check); the authoritative DATA bound lives in the service
  (create_import) and that mutant is KILLED by existing coverage.
- **R270 (eighth window, push defense-in-depth pins)**: batch 33 probed
  the push pipeline. Consent semantics KILLED both ways (revoked treated
  as consent; default-consent). Two defense-in-depth gaps pinned: the
  push model gate (a profile reaching _execute_push with a non-
  talent.application model — only possible past create-validation — must
  fail closed with push_model_unsupported, never push roster rows into an
  ATS) and the PUSH-side mapping version-drift check (pull side was
  pinned; push side was not). Probe-harness note: the drift anchor occurs
  twice (pull+push) — the first probe mutated the pull side and read as a
  false survivor; re-probed the second occurrence via rfind: KILLED.
- **R269 (eighth window, bulk failOnErrors pin + migration check)**:
  batch 32 probed SCIM /Bulk — op-count cap and BulkRequest-schema guard
  KILLED; the failOnErrors non-negative-int validation had no test (a
  negative threshold would stop the batch from the first operation) —
  pinned (-1 and "2" both 400); re-probed KILLED. Also verified the
  migration chain on a scratch database: zero -> head (intg15a00015)
  upgrades cleanly, head downgrades one step and re-upgrades (newest
  migration reversible).
- **R268 (eighth window, totality properties)**: two hypothesis
  properties added over attacker-facing parsers — the SCIM filter parser
  (arbitrary text -> (attr, value) or ScimError 400, nothing else escapes)
  and the egress URL screen (arbitrary text -> normalized URL or
  EgressBlockedError, no IndexError/ValueError parser leak). 300 examples
  each; both hold.
- **R267 (eighth window, full foreground regression)**: post R250-R266
  (4 security fixes, 3 race-proofed caps, sprawl caps, 8 survivor pins,
  ~50 probes) the whole stack re-verified foreground: backend full suite
  in 12 chunks — every chunk zero failures; web 764 Vitest + tsc + ESLint
  clean; live-HTTP E2E lifecycle 62/62; adversarial battery 178/0
  (initial 10 "failures" were the SSRF screen correctly disabled by the
  E2E-only EGRESS_ALLOW_PRIVATE flag — re-run with the production screen
  active: all pass). Runner lesson recorded: `uv run uvicorn` must be
  killed by process group (start_new_session + killpg), else the uvicorn
  child survives the uv parent and a stale server on the port serves the
  next run's requests with the previous env.
- **R266 (eighth window, group-map/mesh/dynreg probe ledger)**: batches
  30-31. KILLED: group_map role mint-ceiling, group-sync admin demotion
  guard, wildcard-matches-internal-events, wildcard-matches-everything,
  dynreg plain-OIDC rejection, dynreg required-keys screen, dynreg empty
  client_id. One EQUIVALENT documented: dropping `role != STUDENT` from
  the group-leave demotion arm only re-assigns STUDENT to an
  already-STUDENT member (identity write, no behavior change).
- **R265 (eighth window, SLO probe ledger + DTD pin)**: batch 29 probed
  the SAML Single Logout validator. Bad-signature and issuer-mismatch
  KILLED. Two layered-defense equivalents documented: dropping the
  unsigned-presence check still rejects (the empty Signature segment
  fails inside the decode try -> slo_signature_invalid), and dropping the
  SigAlg allowlist is absorbed by the hardcoded SHA256 verify. The DTD
  screen however had NO SLO-side test (the assertion-side DTD test does
  not reach this parser) — pinned with `test_slo_dtd_forbidden_even_when_
signed` (valid IdP signature over a DOCTYPE-carrying LogoutRequest ->
  refused); re-probed KILLED.
- **R264 (eighth window, back-channel-logout probe ledger)**: batch 28
  probed the OIDC back-channel logout validator — nonce-prohibition, events
  member, iat freshness and sub requirement all KILLED. Two documented
  EQUIVALENT mutants (layered defenses, outcome already pinned): dropping
  the jti pre-check still rejects replay through the deterministic-key
  unique index + SAVEPOINT (the pre-check is a fast path; the existing
  replay test passes through the IntegrityError layer), and dropping the
  header alg!=RS256 check is absorbed by pyjwt's decode(algorithms=
  ["RS256"]) enforcement (same equivalence class recorded for login
  id_token validation).
- **R263 (eighth window, R262 class — LTI caps)**: LTI registrations had
  no per-org bound (each is a platform trust anchor) and `deployment_ids`
  was inserted row-per-entry with no request bound (a single create could
  park unbounded rows). Added MAX_LTI_REGISTRATIONS_PER_ORG=10 under the
  FOR UPDATE org lock and MAX_DEPLOYMENTS_PER_REGISTRATION=50 as a request
  screen; `test_lti_registration_caps` drives both rejections.
- **R262 (eighth window, sprawl caps — shared-sweep fan-out bound)**: the
  fabric had NO per-org bound on connections, export streams, or sync
  profiles, yet three shared sweeps fan out over those rows for every org
  (half-hourly connection pings, hourly export runs, scheduled syncs) — one
  tenant scripting creates could degrade every tenant's scheduler, and each
  connection also holds credentials (audit surface). Added
  MAX_CONNECTIONS_PER_ORG=20, MAX_STREAMS_PER_ORG=20,
  MAX_SYNC_PROFILES_PER_ORG=50, each enforced count-then-insert under the
  FOR UPDATE org lock (R260 idiom) with stable error codes
  (CONNECTION/EXPORT/SYNC_PROFILE _LIMIT_REACHED). Outcome test
  `test_per_org_sprawl_caps` drives all three to their cap and asserts the
  rejections; full sync/export/races/acceptance suites green.
- **R261 (eighth window, R260 class — cap TOCTOU sweep)**: swept every
  per-org cap in the fabric for the same count-then-insert race. Domains
  (R113) and webhooks already lock; SCIM token create and SSO connection
  create did NOT — two concurrent creates at cap-1 both pass the count and
  exceed the bound (each SCIM token is full provisioning power; each SSO
  connection is a trust anchor). Both now take the FOR UPDATE org lock
  before counting. Races pinned in races_db (exactly one win at cap-1 for
  both) and demonstrated real with the lock removed + adverse scheduling
  injected (both tests then yield cap+1).
- **R260 (eighth window, SECURITY fix — break-glass cap TOCTOU)**:
  `set_break_glass` counted designees and then set the flag with no
  serialization — two concurrent enables at cap-1 both count 1 < 2 and
  yield THREE break-glass members (each one is a password bypass under
  enforced SSO, so the <=2 cap is a security bound). Fixed with the R208
  pattern: a FOR UPDATE lock on the org row serializes count-then-set.
  Race pinned in races_db (`test_break_glass_cap_holds_under_concurrent_
enables`: two gather'd sessions at cap-1 -> exactly one win, final
  count 2) and demonstrated real: with the lock removed and adverse
  scheduling injected after the count, the same test yields 3 designees.
- **R259 (eighth window, SSRF + registry probe ledger)**: batches 26-27
  probed the egress screen itself (userinfo smuggling, non-http(s) scheme,
  port screen, literal private IP, internal TLD/localhost, CGNAT range,
  mixed public+private resolution) and the connector registry (429 retry
  bound, 401/403 ping -> unhealthy, 5xx ping -> unhealthy, empty OneRoster
  token) — 11/11 KILLED with verified failure tails (probe harness now
  asserts test paths exist and prints the pytest tail). Router audit:
  every fabric endpoint across sync/connections/events/export/imports/
  roster carries an owner|admin gate (AST-level sweep, zero missing);
  response schemas carry no ciphertext/token fields by construction.
- **R258 (eighth window, mapping field-cap pin + probe-harness lesson)**:
  batch 25 probed roster (cross-org connection IDOR, bad unenroll policy)
  and NRPS (cross-org resource link, inactive registration, next-link SSRF
  screen) — all KILLED. The mapping probes initially targeted a nonexistent
  test path; pytest's usage-error exit was misread as KILLED (probe-harness
  lesson: a probe must verify the test path collects before trusting a
  nonzero exit — tails are now printed). Re-probed against the real
  coverage (sync_db + core): int-range and 64KB document caps KILLED; the
  MAX_FIELDS cap (DoS bound on per-save compile lists) had NO test —
  pinned with `test_mapping_field_count_cap` (at-cap accepted, cap+1
  rejected); re-probed KILLED.
- **R257 (eighth window, domain-IDOR pin + probe ledger)**: batches 22-24
  probed 16 more mutants across identity (unverified-email auto-link, revoked
  link honored, inactive user, ambiguous multi-member, email hijack), AGS
  (sync-disabled fires, inactive registration, cross-org resource link),
  warehouse (cursor boundary re-export, unsalted/org-unscoped anonymize hash,
  disabled stream runs, empty allowlist), bulk import (formula injection,
  unknown role, duplicate email), domains (freemail claim, pending expiry),
  and SCIM (revoked token authenticates, deactivate no-op) — 15 KILLED by
  existing coverage. ONE survivor: `OrgDomainService.get` org-scoping had no
  test, so org B could in principle read/verify/DELETE org A's domain claim
  (deleting a verified domain drops the victim's SSO enforcement). Pinned
  with `test_domain_cross_org_idor_uniform_404` (get/verify/delete all
  uniform 404); re-probed KILLED.
- **R256 (eighth window, SAML request-id pins)**: batch-21 probes left two
  genuine coverage gaps in `_consume_request_id` — dropping the
  `used_at IS NULL` filter (request-id replay: a fresh assertion reusing an
  already-consumed InResponseTo would log in again) and dropping the
  `sso_connection_id` filter (connection A's request-id satisfying an
  assertion presented to connection B) both SURVIVED. The guards exist in
  code; no test exercised them independently of the assertion-replay cache.
  Pinned with `test_saml_request_id_single_use_and_connection_scoped`
  (second distinct assertion on a consumed InResponseTo -> 401; cross-
  connection presentation -> 401). Both mutants re-probed KILLED. The third
  batch-21 "survivor" (cert-expiry window inverted) was a probe artifact —
  batch21 ran it against sso_db while the sweep test lives in saml_db;
  re-probed against the correct file: KILLED, no change needed.
- **R255 (eighth window, enforce/break-glass pins)**: two unpinned
  directions on the SSO-required gate. Over-enforcement: the gate must key on
  VERIFIED domains only — an org with a merely PENDING claim cannot lock its
  members out of password login. And the break-glass designee cap (≤2, the
  bound on the password-bypass surface) had no test; re-enabling an existing
  designee stays idempotent. Both mutants now killed (plus gate-open).
- **R254 (eighth window, probe ledger)**: 17 more mutants killed —
  PII-purge filters (2), error-report identifier, SCIM filter case, revoked
  links (2), conflict run-attachment + stale-accept guard, NRPS next-link
  screen + page cap, egress scheme allowlist, co-sign rotation window (3:
  infinite window, never-emitted, immediate-keeps-prev). Full suite
  7364/7364 on the R253 HEAD; fabric 325, web 764+tsc+lint, E2E 62,
  adversarial 178, zero tracebacks.
- **R253 (eighth window, SECURITY fix — LTI dynreg platform mix-up,
  mutation-killed)**: the R251/R252 class for dynamic registration — a
  configuration document whose issuer lives on a DIFFERENT origin than the
  admin-pasted URL registers the tool against another platform. Strict
  OIDC-Discovery §4.3 derivation would break real LMSes (Moodle's
  non-standard config path), so the guard is same-ORIGIN (scheme+host):
  cross-origin issuer → 422 before anything is posted. Test-suite variant
  issuers (used to dodge the unique index between sub-cases) moved to
  same-origin path suffixes.
- **R252 (eighth window, SECURITY fix — SAML metadata mix-up,
  mutation-killed)**: the R251 class on the SAML side. `refresh_from_metadata`
  ADOPTED whatever entityID the fetched document carried — a wrong document
  at the metadata URL (multi-tenant host, path confusion) silently re-pointed
  the connection at a different IdP: pinned certs, SSO URL and the issuer
  check all followed the imposter. Fix: a configured entityID must MATCH the
  document's (422 on mismatch, nothing adopted); adoption only when
  previously unset. The rotate test's old expectation (silent overwrite)
  embodied the vulnerable behavior and was rewritten to pin both directions.
- **R251 (eighth window, SECURITY fix — issuer mix-up, mutation-killed)**:
  `_discovery` never validated that the metadata's `issuer` equals the
  configured `oidc_issuer` the discovery URL was derived from (RFC 8414
  §3.3). Since id_token decode validates against `doc["issuer"]`, a
  multi-tenant IdP host (or confused deployment) returning a DIFFERENT
  issuer would make us accept THAT issuer's tokens. Fix: trailing-slash-
  normalized equality check → generic 401 on mismatch; existing flows
  (issuer-consistent) unaffected, SSO file 30/30.
- **R250 (eighth window, IDOR-class survivor pin)**: `resolve_conflict`
  verified the RUN belongs to the org but the RESULT was fetched by id alone
  — removing the `result.run_id == run.id` check let an admin resolve a
  FOREIGN org's conflict row via their own run id. Outcome pin: own-run +
  foreign-result → uniform 404, row untouched. Batches 16–17 also killed 7:
  PII-purge terminal-only + retention window, error-report identifier, SCIM
  filter case-insensitivity, revoked-link listing, wrong-org unlink,
  conflict-row run attachment, stale accept_theirs guard.
- **R249 (seventh window, final foreground tally)**: four complete
  foreground passes of the full API suite on successive HEADs
  (7348 → 7356 → 7357 → 7361, zero failures), fabric suite to 322, web
  764+tsc+lint ×4, E2E 62 ×4, adversarial 178 ×4 with zero API tracebacks.
  Window-7 totals: ~60 mutants killed, 13 new survivor-pin tests
  (R239–R241, R243–R245, R247–R248), 6 documented equivalents, 3 registry
  drift guards, 1 harness-hygiene fix. All executed as sequential foreground
  commands per operator instruction.
- **R248 (seventh window, survivor pins ×4)**: four more unpinned
  properties: bulk-replay per-call cap (monkeypatched cap=2, 3 exhausted →
  exactly 2 clones), single-replay 409 on a DISABLED subscription (replay
  must not resurrect silenced endpoints), to_int bool rejection
  (outcome-pinned; the explicit isinstance guard is equivalent via
  int(str(bool)) ValueError), and LTI deep-link `data` verbatim round-trip
  (present when sent, absent when not). Batches 13–15 killed 10 more:
  all five report/stat counters, replay-clone byte fidelity, first-dispatch
  archive gate, bulk-replay covered-skip, signature v1 prefix, to_int range.
- **R247 (seventh window, survivor pin)**: a frozen webhook-timestamp (ts=0)
  survived — the signature stays internally consistent, but receiver-side
  Standard-Webhooks replay protection depends on a FRESH timestamp. New
  freshness assertion on build_delivery_headers. Batch also killed:
  signature-header swap, org-salt unbinding, revoked-link resolution.
- **R246 (seventh window, single-chat foreground ledger)**: entire 5-hour
  verification executed as sequential FOREGROUND commands (no background
  tasks/monitors). Round 1: full suite 7348 green in 11 chunked runs, E2E
  62, adversarial 178. Probe batches 7–11 killed 19 more mutants and pinned
  5 survivors as new tests (R239 expr-cap, R240 unsolicited-SAML, R241
  auto-disable negative, R243 scheduler negatives ×3, R244 NRPS privilege
  ceiling + cert-parse 422, R245 fingerprint version binding); equivalents
  documented (export-sweep filters double-gated). Round 2 on the final HEAD:
  full suite 7356 green, fabric 317, web 764+tsc+lint, E2E 62, adversarial
  178 — zero failures, zero tracebacks.
- **R245 (seventh window, upgrade-safety pin)**: the dry-run fingerprint's
  template-version binding had no pin — dropping the version from the hash
  only manifests ACROSS a template upgrade (stale pre-upgrade previews would
  commit under new semantics). Direct hash-input test added. Batch 10 also
  killed: event-size cap widening, webhook signing secret swap, SCIM string
  "False" deactivation.
- **R244 (seventh window, privilege-escalation pin)**: the NRPS ceiling test
  asserted only the POSITIVE direction (instructor member → instructor) — a
  mutant minting instructor for EVERY member (privilege escalation) survived.
  Complementary assertion added: the non-instructor member gets the
  registration's default role. Also pinned: an unparseable pinned certificate
  is a clean 422 at create (previously unreached negative path). Batch 9
  re-probe: NRPS role ceiling, inactive-member skip, cert parse, enforce-SSO
  break-glass gate — 4/4 killed.
- **R243 (seventh window, scheduler-negative pins)**: the schedulers' NEGATIVE
  space was untested — `manual` streams/profiles never auto-running and
  disabled streams being skipped had no pins (only the positive "due daily
  runs" direction). Three new outcome tests; probe dispositions: the two
  export-filter mutants are double-gated equivalents (the loop's
  cadence-lookup `continue` and run_export's own DISABLED 409 absorb them),
  while the sync-profile filter mutant and the invalid-unenroll-policy 422
  are genuinely killed by the new pins. Queue-dedup mutant also killed.
- **R242 (seventh window, foreground sweep record)**: single-chat foreground
  verification pass (no background tasks): full API suite 7348/7348 in 8+3
  chunked foreground runs, E2E 62/62, adversarial 178/178 (zero tracebacks),
  then continued clean-harness probes — LTI launch-state reuse, engine
  backfill-cursor/dup-external-id/delta-tombstone, SCIM revoked-token +
  group-map validation, CSV-injection guard, atomic-failure status, outbox
  unknown-topic dead-letter: 10 more KILLED (one malformed probe on the
  export update path discarded as invalid, create-path already pinned).
- **R241 (seventh window, survivor pin)**: the 5-day auto-disable rule was
  pinned only in the POSITIVE direction — shrinking the window to 0 days
  (every first exhaustion disables the endpoint) survived the suite. New
  negative-direction test: a freshly-exhausted delivery must leave the
  subscription ACTIVE. Batch also killed: retention-deletes-pending,
  internal-events-wildcard-routable, dynreg platform-claim + egress-screen
  (4).
- **R239/R240 (seventh window, survivor pins — foreground sweep)**: two more
  survivors pinned. R239: no test bounded a single JMESPath expression
  (MAX_EXPR_LEN) — the 64KB document cap only partially shadows it; a direct
  validate_document test now kills the widened-cap mutant. R240: an
  assertion with NO InResponseTo (IdP-initiated SSO) relied on the
  downstream consume gate; an outcome-level test (validly signed, real
  outstanding request, attribute stripped pre-signing) pins the 401.
  Foreground batch results: mapping (4 killed + R239), connections state
  machine (3 killed — the two-strike rule pinned by the health file),
  domains (freemail/claim + verified-holder killed; freemail DISCOVERY
  short-circuit is equivalent via the claim gate), SCIM bulk (3 killed),
  AGS gating (3 killed incl. score clamp), SAML relay-state binding killed.
- **R238 (seventh window, test-infra hardening)**: the health-sweep
  transition test swept the WHOLE shared dev DB (limit=100_000) with the real
  connector registry — garbage connections from prior runs did real outbound
  pings (5s connect timeouts), and under DB contention the test blew its 300s
  timeout. Hermetic fix: swap the ENTIRE connector registry for instant fakes
  during the test (full save/restore), and scope the parked-not-pinged
  counter to the test's own connection id (prior-run oneroster leftovers hit
  the counting fake too). Health file: 108s → 9s; roster/consent probes this
  sweep (role-overwrite, guess-on-ambiguity, consent gate, revoked-counts — 4) all KILLED. Fabric 309/309.
- **R237 (seventh window, unreached-branch pin)**: no test exercised a SAML
  connection whose pinned-cert list is EMPTY — the branch guarding against
  "verify with no pinned certs" (where a bad fallback could trust the
  embedded KeyInfo cert) was dead in the suite. New outcome-level test: a
  validly IdP-signed assertion against an empty cert list is rejected 401.
  Probing `certs=[""]` proved signxml rejects an empty cert rather than
  falling back (equivalent mutant) — the property now stays pinned even if
  the library's semantics ever change. Outbox worker probes (handler
  savepoint, dead-letter threshold — 2) and XSW signed-subtree (1) also
  KILLED. Window-7 harness totals: 29 killed, 2 equivalent.
- **R236 (seventh window, clean-harness sweep continued)**: identity takeover
  guards (unverified-email, foreign-domain, multi-match, JIT ceiling — 4),
  LTI launch guards (nonce, deployment allowlist, azp — 3), OIDC login-state
  (reuse, expiry, PKCE verifier — 3), import fingerprint gate (1): 11 more
  KILLED. One documented EQUIVALENT survivor: removing LTI's alg pre-check
  leaves pyjwt's `algorithms=["RS256"]` enforcing the same property (the
  existing HS256 key-confusion test proves rejection at the outcome level);
  the pre-check stays as defense-in-depth with a cleaner error code.
  Window-7 totals: 24 killed, 1 equivalent.
- **R235 (seventh window, clean-harness verification record)**: after the
  R234 pycache fix, re-probed the security cores with the hygienic harness:
  export projection (drop/hash/salt/allowlist-bypass — 4), webhook signature
  composition (1), SCIM deprovision (session revoke, membership archive — 2),
  SAML condition window (expiry, no-expiry, audience — 3), delivery ladder
  boundaries (3). 13/13 KILLED, zero survivors; the sole historical survivor
  (3xx success window) is now pinned by R234's test.
- **R234 (seventh window, survivor pin + methodology fix)**: no test pinned
  "a 3xx is a delivery FAILURE" (Standard Webhooks requires 2xx; EgressClient
  never follows redirects, so a 302 is not acceptance). New test: a 302
  records http_302 and schedules a retry — the widened `<400` success-window
  mutant now dies. The hunt also exposed a MUTATION-HARNESS trap: restoring a
  mutated source via shutil.move can leave the MUTANT'S .pyc alive (mtime
  second-granularity collision), silently poisoning subsequent runs — probes
  must clear **pycache** after write AND after restore. (Timeline audit:
  all recorded suite results predate the one polluted window.)
- **R233 (seventh window, R231 class)**: registry-coherence guards — a
  schedule added to SYNC_SCHEDULES/EXPORT_SCHEDULES without a sweep cadence
  entry is accepted by the API but NEVER auto-runs (silent no-op schedule);
  the three import-kind registries (IMPORT_KINDS, TEMPLATE_VERSIONS,
  KIND_SPECS) must agree. Set-equality tests for all of them.
- **R232 (seventh window, R231 class)**: `MODEL_REQUIRED_KEYS` guard — a
  canonical model missing from the dict makes strict_schema silently
  validate nothing (frozenset() fallback). Bidirectional set-equality test
  (no missing models, no stray entries, no empty key sets).
- **R231 (seventh window, drift guard — probe-killed)**: the event catalog's
  `direct` list was hand-maintained inside the endpoint — a new facade
  emission without a catalog entry would be silently undiscoverable in the
  subscription UI. Hoisted to module-level `DIRECT_EMISSIONS` plus a
  source-scan guard test: every bare mesh-event name emitted anywhere
  (emit_event literals, SCIM `_audit` literals, INTERNAL_EVENT_PREFIX
  f-strings) must appear in legacy ∪ DIRECT_EMISSIONS ∪ internal-alertable,
  and DIRECT_EMISSIONS may contain no phantom entries. Injecting an
  uncatalogued emit fails the test.
- **R230 (sixth window, R229 class)**: upload and commit on the data page
  never invalidated the `intg-imports` history list rendered alongside —
  stale until manual refresh. Both mutations invalidate it now. (Staleness
  sweep across all five fabric pages: every create/mutate now invalidates
  every co-rendered list it affects.)
- **R229 (sixth window, UI staleness fix)**: resolving an identity-queue item
  with action `link` CREATES an identity link, but the page only invalidated
  the queue query — the links table alongside it showed stale data until a
  manual refresh. Both queries invalidate now.
- **R228 (sixth window, R226 class — domain sweep)**: the quarter-hourly
  pending-domain sweep does up to 200 slow DNS lookups per tick with no cron
  timeout margin; a kill rolled back every verification already made. Commit
  per verified row + cron timeout=1800. Completes the sweep-durability class:
  health (R226), metadata (R227), domains (R228); retention already
  committed per batch, exports per run (R208 lock).
- **R227 (sixth window, R226 class — metadata sweep)**: the daily SAML
  metadata refresh made one slow outbound fetch per connection with a single
  trailing commit — a job-timeout kill rolled back every cert rotation
  already applied. Now commits per connection (failures roll back only their
  own partial state) and the cron got timeout=1800.
- **R226 (sixth window, fleet-scale availability fix)**: the half-hourly
  health sweep pinged EVERY active/degraded connection serially (up to ~20s
  each) with ONE trailing commit — at fleet scale it outlived the cron job
  timeout and the kill rolled the entire sweep back, so health never decayed.
  Now each tick takes a stalest-first slice (updated_at ascending; a ping
  bumps the row to the back, so rotation is fair), commits PER CONNECTION
  (a mid-sweep kill keeps completed work), and the cron got timeout=1800.
  Deterministic slice test: two epoch-dated connections, limit=1 pings
  exactly the stalest, the next tick pings the other.
- **R225 (sixth window, admin-UX parity fix)**: rotating credentials reset an
  ERRORED connection to pending (fresh ping), but editing the other two
  fixable inputs — config or base_url — did not: the connection stayed parked
  unless the admin also knew to flip status manually. `update()` now applies
  the same error→pending reset on a config/base_url edit; a pure rename never
  touches status.
- **R224 (sixth window, protocol-correctness fix — mutation-killed)**: a
  410 Gone from a webhook endpoint was retried through the full 8-attempt
  ladder and only counted toward the 5-day auto-disable window — but 410 is
  the RECEIVER unsubscribing (Svix convention: disable immediately). Now the
  first 410 cancels the delivery, deactivates the subscription, and emits
  `integration.subscription.auto_disabled` with reason `endpoint_gone`
  (same alert channel as the 5-day rule). Replayed attempts no-op.
- **R223 (sixth window, R218 class — roster preview)**: the roster import
  preview paid ~3 point SELECTs per row (cohort by slug, user by email,
  membership). Batched into IN(500) maps (`_roster_preview_maps`) consumed by
  a pure per-row function; `_preview_roster_row` kept for the commit path's
  per-row savepoint semantics. N+1 sweep of the fabric now complete: pull
  engine (R218), push (R219), roster provisioning (R220), SCIM list (R221),
  user-import preview (R222), roster-import preview (R223).
- **R222 (sixth window, R218 class — import preview)**: `_preview_user_rows`
  runs INLINE in the upload request and paid 2 point SELECTs per row — 20k
  round-trips on a 10k-row file, all inside one HTTP request. Batched into
  IN(500) user-by-email + membership queries; per-row logic unchanged.
  Import file 26/26.
- **R221 (sixth window, R218 class — SCIM side)**: the SCIM user list built
  each row's resource with a per-row `_link_for` point SELECT (up to 200 per
  page; IdPs page the whole directory nightly → 10k extra round-trips per
  sweep on a 10k-user org). One IN(...) link query per page now. SCIM file
  28/28.
- **R220 (sixth window, R218 class — roster side)**: `_provision_enrollments`
  paid ~3 point SELECTs per enrollment (identity link, staged roster.user,
  plus the tombstone-path link lookup) — 15k round-trips for a 5k-enrollment
  school. Prefetched into bounded IN(500) maps handed to `_resolve_user`
  (fallback point SELECTs kept for direct callers); successful resolutions
  backfill the link map so repeat users short-circuit.
- **R219 (sixth window, R218 class — push side)**: `_execute_push` did the
  same per-record staged point SELECT; now prefetched in bounded IN(500)
  batches before the loop. Push + sync files 40/40.
- **R218 (sixth window, scale fix — mutation-killed)**: the pull engine
  looked up each record's staged row with a point SELECT — an N+1 of 500
  round-trips per batch (minutes of pure latency on a 1M-record enterprise
  sync). Fix: prefetch the chunk's staged rows in ONE `IN (...)` query and
  hand the map to `_apply_record` (the point SELECT stays as the fallback for
  direct callers). Query-count test at the cursor level: 12 records in
  chunks of 3 issue ≤6 staged-table SELECTs; the per-record version (13+)
  fails it.
- **R217 (sixth window, OOM fix — mutation-killed)**: the EgressClient
  response-size cap ran AFTER httpx buffered the entire body
  (`len(resp.content) > cap`) — a hostile or misconfigured upstream returning
  gigabytes OOM'd the worker before the "cap" ever fired. Fix: stream via
  `build_request`+`send(stream=True)`; reject a declared oversized
  Content-Length before reading any body, count chunks and abort the
  connection at the cap otherwise, then hand back a normal buffered Response.
  Test proves zero body reads on declared reject, mid-stream abort (≤20 of 64
  chunks) on chunked overflow, and an unchanged small-response path; the
  buffered-check mutant fails it.
- **R216 (sixth window, availability fix)**: the OneRoster and CRM readers'
  offset-pagination loops had NO page bound (NRPS already capped at 25) — a
  misbehaving server that ignores `offset` (always returns a full page) made
  the sync run INFINITE: the heartbeat kept refreshing so the stale-run
  reaper never fired, and staged writes churned forever. Fix: MAX_READ_PAGES
  = 10,000 (1M records at the default page size); past it the run fails
  cleanly with CONNECTION_PING_FAILED. Test: an offset-ignoring fake server
  with the cap monkeypatched to 4 — exactly 4 pages yielded, then AppError.
- **R215 (sixth window, DATA-LOSS fix — mutation-killed)**: the pull engine
  processed only `records[: BATCH_SIZE * 2]` of each connector page but
  counted ALL of them in `stats.read` and advanced the cursor past the whole
  page — an overfull page (>1000 records in one yield) silently LOST its
  tail forever, and a backfill then TOMBSTONED those very records (they never
  reached the seen-set). Fix: process every record, chunked into BATCH_SIZE
  sub-transactions (interim commits hold the cursor); the cursor advances
  only once the WHOLE page is committed, preserving §11.3 crash-replay
  idempotency. Test monkeypatches BATCH_SIZE=3 with an 8-record page:
  8 staged, 0 tombstoned; restoring the old cap fails it.
- **R214 (fifth window, parity hardening)**: the two most expensive trigger
  endpoints had NO rate limit while the comparable sync trigger did (R160
  family): `POST /export-streams/{id}/run` (full warehouse export) and
  `POST /connections/{id}/provision-roster` (walks every staged
  class/enrollment). Both now `rate_limit(10, 60)` — admin-gated already, but
  a buggy client could hammer them.
- **R213 (fifth window, R110-class fix — the ironic one)**: `create_job`'s
  idempotency key is FOR absorbing concurrent duplicate submissions, yet the
  check-then-add against `uq_intg_import_idem` meant exactly that race 500'd
  the loser at a bare flush. Fix: savepoint INSERT; on collision re-select
  and return the winner's job (identical to the sequential idempotent path).
  Systematic sweep of every `unique=True` table in the integrations models
  confirms the remaining insert sites are guarded (connections R-early,
  mapping R173, export streams, LTI tool key R111, identity links, SCIM
  users/groups/members, EventDelivery on_conflict, domains R207, credentials
  R212).
- **R212 (fifth window, R110-class fix)**: `set_credential` was
  check-then-add against the UNIQUE 1:1 credential envelope
  (connection_id unique) — a concurrent FIRST-TIME credential set's loser hit
  IntegrityError at a bare flush (500 + poisoned session). Fix:
  savepoint-wrapped INSERT; on collision fall through to rotate-in-place on
  the winner's row (last writer wins, identical to the update branch).
  Outcome-scoped two-session test (single-loop interleave limit stated, per
  R199/R207 precedent).
- **R211 (fifth window, R87/R210-class fix — mutation-killed)**: `emit_event`
  size-checked data with bare `json.dumps` (allow_nan=True, no default): a
  NaN/Infinity passed the check and failed at the JSONB flush — INSIDE the
  caller's domain transaction (poisoned session, domain write 500); a
  datetime/Decimal in data raised TypeError from the size check itself. Fix:
  `json.dumps(payload, allow_nan=False)` + catch → clean 422
  EVENT_DATA_INVALID before anything is added to the session.
- **R210 (fifth window, R87-class fix — mutation-killed)**: `apply_mapping`'s
  non-finite gate only checked a TOP-LEVEL float. `json.loads` — and therefore
  every connector's `resp.json()` — accepts `NaN`/`Infinity`, so a provider
  can hand us a non-finite float nested inside an object or list; it passed
  validation into the mapped payload and the JSONB staging write rejected it
  mid-run (500). Fix: `_has_non_finite` recursive scan; nested NaN/Inf now
  yields a clean per-field `non_finite` conflict.
- **R209 (fifth window, governance fix — mutation-killed)**: whole-class SIS
  offboarding silently stopped removing members. The backfill tombstones the
  class AND its enrollments together, but the unenroll pass looked the cohort
  up only in the staged-ACTIVE class map — tombstoned-class enrollments hit
  `cohort_id is None → continue` and memberships lingered forever. Fix: the
  unenroll branch falls back to the connection's backlink map (every cohort
  this connection ever provisioned); the ACTIVE path intentionally keeps
  requiring a staged-active class (an active enrollment into a tombstoned
  class stays a missing_reference conflict, never a silent write).
- **R208 (fifth window, concurrency fix — mutation-killed)**: `run_export`
  had no per-stream serialization: a manual trigger racing the hourly sweep
  (or a double-trigger) read the SAME cursor — both re-export the span, and
  the last committer can REGRESS `stream.cursor` (its last_cursor may be
  older), so the next run re-exports the whole span again. Fix: `SELECT ...
FOR UPDATE` on the stream row + refresh, making read-cursor → export →
  advance-cursor atomic per stream. The race test uses a slow writer to force
  the interleave and asserts [0, 3] row counts — removing the lock makes it
  fail (genuinely killed, unlike the single-loop-limited R207/R199 tests).
- **R207 (fifth window, concurrency fix)**: `OrgDomainService.claim` capped
  domains with a bare COUNT (TOCTOU — concurrent claims could exceed the
  20-domain cap) and inserted after a check-then-add dup SELECT against
  `uq_intg_domain_org` — a concurrent same-(org,domain) claim's loser raised
  IntegrityError at a bare flush: 500 + poisoned session (R110 class). Fix:
  `SELECT ... FOR UPDATE` on the Org row (mirrors webhook defect #102) so
  same-org claimers serialize, plus savepoint-wrapped INSERT with
  IntegrityError → idempotent re-select of the winner's row. Outcome-scoped
  two-session test (docstring states the single-loop interleave limit, per
  the R199 precedent).
- **R206 (fifth window, flake root-cause fix)**: the recurring
  `test_attempt_response_snippet_captured_sanitized_and_capped` full-suite
  failure (survived both R193 URL-scoping and R204 purge) was structural: the
  test asserted an exact [500, 200] attempt sequence but drove it through the
  GLOBAL `_drain`, which shares the dev DB's leftover outbox/delivery state.
  Rewritten self-contained: fan out its own event via `handle_event_created`,
  then call `handle_delivery_attempt` directly on its own delivery (500 →
  force due → 200). No dependence on global drain order; outbox mechanics
  remain covered by the dedicated outbox tests. Fabric 290/290.
- **R205 (fifth window, silent-data-drop fix)**: a CSV with two columns
  mapping to the same canonical field (duplicate header, or a header_map that
  aliases two source columns onto one canonical) made csv.DictReader silently
  keep only the LAST value — a silent data drop. parse_users_csv now detects
  duplicate KNOWN-canonical columns and rejects the file with a clear
  `duplicate_column` error.
- **R203 (fifth window, observability coverage)**: test pins that an export
  over an empty source still writes a manifest (row_count=0, parts=[]) and
  succeeds — the run stays observable in the warehouse, never a silent no-op.
- **R202 (fifth window, push credential coverage)**: R194 fixed both the
  read AND push ctx; added a push-path test (secret-capturing ATS connector)
  proving the decrypted api_key reaches the connector during write — the read
  path had R194's test, the push path now has its own.
- **R201 (fifth window, probe over R196/R198)**: mutation probe killed the
  preview-direction and atomic-status mutants; the surviving "preview limit
  not enforced across batches" mutant was a REAL coverage gap (the test used
  one batch, so the per-batch outer break was never exercised) — closed with
  a two-batch limit test (limit=3, two batches of 3 → exactly 3, no spill).
- **R199 (fifth window, replay-cache concurrency defense)**: the SAML
  assertion and OIDC back-channel-logout replay caches used check-then-add on
  a deterministic key; under TRUE parallelism (two workers, same assertion/
  logout token) the unique-violation loser would 500 instead of a clean
  replay rejection. Both INSERTs now run in a savepoint → the loser is a
  clean assertion_replayed / logout_token_replayed (same add-before-savepoint
  discipline as R167/R172/R176). A concurrent test confirms the clean
  outcome (the common asyncio-serialized path hits the SELECT guard; the
  savepoint covers the true-parallel INSERT collision).
- **R198 (fifth window, atomic-import status bug)**: an atomic import that
  failed during APPLY (not validation) set status='failed' then RAISED — the
  request-boundary rollback erased the status, leaving the job stuck at
  'previewed' with no failure detail (while the validation-error path
  correctly returned status='failed'). Rewrote atomic apply to run the whole
  loop in ONE savepoint: a failure rolls back all partial data but the outer
  transaction persists status='failed' + the failing-row reason, and returns
  (consistent with the validation path). Test asserts the failed status
  survives a commit and nothing was applied.
- **R197 (fifth window, UI)**: a "Dry-run" button on each pull sync profile
  wires to the R196 preview endpoint and toasts the pulled count (nothing
  staged) — an admin validates a connection's live read before scheduling.
- **R196 (fifth window, world-class feature)**: sync dry-run preview —
  `POST /sync-profiles/{id}/preview` reads the first few records from the
  connector (with REAL credentials, now that R194 wired them) and shows the
  raw records + how the profile's mapping transforms them, with no staging /
  cursor / writes. This is the inbound analog of mapping-preview (which only
  works on hand-pasted samples) and the Fivetran/Airbyte "test connection +
  preview data" flow an admin needs before scheduling a sync. Pull-only
  (422 on push), rate-limited (outbound read), 1-20 records.
- **R195 (fifth window, regression guard)**: a source-level contract test
  asserts every ConnCtx built in the sync engine passes `_secret_loader`, so
  a future construction site that forgets it (reintroducing R194) is caught.
- **R194 (fifth window, HIGH-SEVERITY production bug)**: sync runs built the
  connector ConnCtx WITHOUT a `_secret_loader`, so `ctx.get_secret()` returned
  `{}` — every real connector (OneRoster OAuth client-credentials, generic
  CRM api_key, generic ATS) authenticated with an EMPTY secret and would
  401/403 on every scheduled or triggered sync, while `ping` (which DID build
  the loader) reported the connection healthy. Invisible to the suite because
  all sync tests use a FakeConnector that never calls get_secret. Fixed: both
  the read and push paths now build the ConnCtx with the same credential
  loader ping uses (`_secret_loader_for`). Test with a secret-capturing
  connector asserts the decrypted client_secret reaches the connector
  (reverting the fix fails it).

- **R170 (fourth window, UI)**: a "Download template" button on the import
  panel pulls the current kind's CSV template via the R169 endpoint, so an
  admin can grab the exact columns before preparing a file.
- **R186-R187 (fourth window, probes)**: export cadence 3/3 and mapping
  validation 4/4 mutants killed — R183 and R164 fully pinned.
- **Marathon4 verification (late-window, R180-R192)**: fabric 281/281, web
  764/764, live E2E 62/62, consumers (controlplane/billing/webhooks) green;
  every new fix mutation- or revert-probed (export cadence 3/3, mapping 4/4,
  R188 capacity 2/2). Audited clean with no further defects: LTI DL/client-
  assertion JWT (iat/exp 300s + nonce/jti), SAML+metadata XML parse (XXE/
  entity-bomb safe), SCIM token sha256-hash compare (timing-safe), webhook
  event-pattern validation, DNS verify timeout+exception-safe. All unique
  create/rename paths uniformly 409-not-500 under concurrency.
- **R192 (fourth window, rename symmetry complete)**: SCIM group PATCH
  rename now isolates its flush in a savepoint too — a concurrent rename
  collision returns a clean SCIM 409, session stays usable for the member
  delta. All rename/create unique paths across the fabric are now uniformly
  409-not-500 under concurrency (connections R172/R182, mappings R173, SCIM
  user R167 / group create R176 / group rename R192).
- **R189 (fourth window, KNOWN GAP documented, not changed)**: bulk user
  import reimplements OrgMember creation and so does NOT pass through the
  §2.5 seat-quota funnel (issue #27) that the interactive add_member enforces
  — a large import can over-provision a tenant past its seat entitlement.
  This was INVESTIGATED and left as a documented gap rather than changed:
  enforcing it (verified locally) breaks the established import test contract
  (imports currently always succeed regardless of plan) and the correct
  behavior — hard-block at cap vs over-provision-then-reconcile-at-billing —
  is a policy decision owned by issue #27, not safe to decide unilaterally
  in a hardening pass. Recommendation + code pointer left in
  bulk_import._apply_row; cohort capacity (R188, a §43-local invariant) WAS
  enforced because it is unambiguous and self-contained.
- **R188 (fourth window, capacity bypass)**: the roster import applied
  CohortMember directly, BYPASSING CohortService's max_learners check — a
  bulk import could overfill a capped cohort past what interactive enroll
  allows. `_apply_roster_row` now counts learners and records a cohort_full
  row error when at capacity (partial mode lands the rest). Test: max=1,
  import 2 → one enrolled, one errored, never overfilled.
- **R185 (fourth window, scheduling bug)**: the export sweep cron was
  `hour=2` (once a day), so R183's `hourly` streams would have silently run
  only daily. Changed to run every hour (minute 47); the per-stream cadence
  check still bounds daily streams to one run/day. A cron-registry test now
  asserts the export sweep is not hour-pinned (revert fails it).
- **R184 (fourth window, UI)**: export-stream create form gains a schedule
  selector (manual/hourly/daily) so the R183 cadences are reachable from the
  admin surface.
- **R183 (fourth window, feature parity)**: warehouse export streams gain an
  `hourly` schedule (sync already had it); `sweep_scheduled_exports` is now
  cadence-aware (per-schedule timedelta: hourly 1h, daily 1d, manual never)
  instead of a hardcoded 1-day check. Test proves hourly re-runs past the
  hour but not within it, and not on the daily cadence.
- **R182 (fourth window, rename-collision symmetry)**: connection UPDATE
  rename now wraps its flush in a savepoint too — renaming onto an existing
  name returns the clean CONNECTION_NAME_TAKEN 409 and leaves the session
  usable (follow-up write in the same session still commits), matching the
  create-path guard. Completes uniform unique-violation handling on the
  connection surface (create R172 + rename R182).

- **Marathon4 verification (mid-window checkpoint R155-R179)**: fabric suite
  277/277, web 764/764, live E2E 62/62, each changed area mutation- or
  revert-probed. Two production-500 classes closed fabric-wide this window —
  add-before-savepoint (JIT user/member, SCIM user/group, connection,
  mapping: R166/166b/167/172/173/176) and naive-datetime compare (SAML,
  echo, sync clock: R177/178/179) — plus DLQ bulk replay, SCIM SQL paging,
  retention index, rate-limit sweep, SAML replay-cache purge, connection
  cascade-delete guard, and Part K template download.

- **R179 (fourth window, production 500 — external naive timestamp)**: the
  clock-conflict resolver compared `theirs_ts > ours_ts` where `theirs`
  comes from EXTERNAL provider data; a provider sending a naive `updated_at`
  (no Z/offset) made that a naive-vs-aware comparison → TypeError → uncaught
  500 mid-sync. `_ts` now forces UTC on naive input. Test pins it (revert
  fails). This closes the fromisoformat-then-compare class across the fabric
  (SAML R177, echo R178, sync clock R179; OIDC/LTI use int epochs; sso_admin
  cert-expiry already guarded).
- **R178 (fourth window, defense-in-depth)**: the echo-suppression read of
  `last_outbound.written_at` (always written aware by us) now also catches
  TypeError and normalizes a naive value to UTC — a legacy/tampered naive
  row can't 500 a sync run via naive-vs-aware subtraction. Same lesson as
  R177, applied preventively to the one other fromisoformat-then-subtract.
- **R177 (fourth window, production 500 — naive timestamp)**: a
  non-compliant IdP sending a SAML assertion timestamp WITHOUT a Z/offset
  parsed to a naive datetime; comparing it against the aware `now` raised
  TypeError (not the ValueError the guard caught) → uncaught 500. `_parse_time`
  now forces UTC on naive input, so a malformed timestamp becomes a clean
  SSO_ASSERTION_INVALID 403. Test pins it (reverting the fix fails the test).
- **R176 (fourth window, add-before-savepoint #8 — SCIM groups)**: the SCIM
  group create path gets the same savepoint + clean 409 guard as create-user
  (R167); concurrent same-displayName creates now return SCIM 409 uniqueness,
  not a 500. The whole SCIM write surface is now uniformly race-safe.
- **R175 (fourth window, probe over R172-R174)**: 4 mutants — the lone
  survivor was a coverage gap (connection delete tested `running` but not a
  `queued` run, which a worker could claim right after the check), closed
  with a queued-run assertion. 4/4 killed on re-probe.
- **R174 (fourth window, cascade-delete integrity)**: deleting a connection
  cascade-deletes its sync profiles AND their runs (FK CASCADE). A LIVE run
  would be ripped out from under the worker mid-pass, so connection delete
  now refuses with CONNECTION_BUSY (409) while any of its profiles has a
  queued/running run — the same discipline profile-delete already had. Test
  covers refuse-while-live then delete-after-terminal (+ cascade cleanup).
- **R173 (fourth window, add-before-savepoint #7 — mappings)**: the last
  check-then-add create path (mapping profiles, uq_intg_mapping_org_name)
  got the same savepoint + clean 409 guard; race-tested 3x. A full sweep of
  (org,name)-unique creates now shows all guarded — connections (R172),
  mappings (R173), export streams + sync profiles (already begin_nested),
  cohort members (CohortService), SCIM group members (on_conflict), domains
  (R113). SCIM tokens have no name-uniqueness so no hazard.
- **R172 (fourth window, add-before-savepoint #6 — connections)**: the
  connection create path had the same shape (dup-SELECT then add+flush); two
  concurrent same-name creates raced to INSERT (uq_intg_conn_org_name). The
  INSERT now runs in a savepoint and the loser returns the same clean
  CONNECTION_NAME_TAKEN 409, not a 500. Race-tested 3x. (update-rename's
  pre-check covers the far rarer simultaneous-rename collision.)
- **R169 (fourth window, Part K template download)**: `GET /imports/template
?kind=&format=` serves a blank, versioned template (ordered header, required
  columns first, + one worked example) per kind in CSV or JSON — the piece
  Part K's "versioned CSV/JSON templates" implied but never exposed. The
  example row round-trips back through the parser with zero errors.
- **R167 (fourth window, add-before-savepoint #5 — SCIM)**: SCIM create-user
  INSERT now runs in a savepoint; a concurrent same-userName loser returns a
  proper SCIM 409 uniqueness error, not a raw 500. Repo-wide add-site sweep
  confirmed the rest already guarded.
- **R168 (fourth window, test isolation)**: the response-snippet test clears
  pending outbox first so its exact [500,200] egress sequence isn't consumed
  by foreign backlog in the global drain.
- **R166 (fourth window, production 500 — add-before-savepoint #4)**: a
  TRUE-concurrency race test over JIT provisioning exposed a fourth
  instance of the marathon-2 bug class — two concurrent first-time SSO
  logins for the same brand-new verified email both took the JIT branch and
  raced to INSERT `users.email`; the unique-violation loser's session was
  poisoned → 500. Fixed: the user INSERT now runs inside `begin_nested()`,
  and on IntegrityError the loser rolls back just that statement and
  re-selects the winner's row (inactive → the same admin-confirmation 403).
  3x stable.
  The membership INSERT in the same method had the identical hazard
  (uq_org_member on a concurrent login of an existing user into one org) and
  got the same savepoint guard; both paths race-tested 3x stable.

- **R165 (fourth window, unbounded-growth fix)**: the SAML assertion replay
  cache reuses the login-state table; only the OIDC authorize endpoint
  purged expired rows, so a SAML-ONLY tenant's replay cache grew forever.
  `build_authn_redirect` now does the same opportunistic day-old purge.

- **R164 (fourth window, input bounds)**: mapping field `transform` lists
  are now length-capped (MAX_TRANSFORMS=10) and type-guarded (a non-list
  value is a validation error, not a char-by-char iteration) — closing the
  last unbounded dimension in an otherwise fully-bounded mapping validator.

- **R163 (fourth window, index)**: the nightly retention sweep deletes
  terminal deliveries by (status, created_at) across all subscriptions; the
  existing (subscription_id, …) index can't serve that, so it full-scanned.
  Added `ix_intg_delivery_status_created` (intg15, reversible).

- **R162 (fourth window, scalability)**: SCIM User/Group list now pages at
  the SQL level (offset/limit + a separate count) instead of materializing
  every row and slicing in Python — a large tenant's IdP paging through the
  whole directory was O(n) rows loaded per page (O(n²) total). Test asserts
  stable totals, non-overlapping pages, and the count=0 total-probe.

- **R161 (fourth window)**: connection ping triggers an outbound call, so
  it gains a 20/60s limit too (throttles SSRF-probe attempts); folded into
  the rate-limit coverage contract test.

- **R160 (fourth window, rate-limit sweep)**: the other write-amplifying /
  provisioning fabric routes — import upload, import commit, sync run — gain
  30/60s rate limits (there is no global limiter middleware; each router
  self-limits). A contract test asserts every one of these routes carries a
  rate_limit dependency so a regression can't silently drop it.

- **R159 (fourth window)**: the bulk replay-exhausted endpoint is write-
  amplifying (up to 500 enqueues per call), so it now carries a 10/60s
  rate limit like the other mutating fabric routes.

- **R157 (fourth window, UI)**: each subscription card gets a "Replay
  exhausted" action wired to the R155 endpoint (toasts the requeued count)
  so operators can recover a backlog without the CLI.

- **R156 (fourth window, e2e hygiene)**: live E2E exercises the bulk-replay
  endpoint and now DELETEs the webhook subscription it created (same
  cleanup discipline as the R150 domain fix) — repeated e2e runs no longer
  accumulate active subscriptions that pollute the shared dev Postgres.
  E2E 62/62.

- **R155 (fourth window, DLQ bulk recovery)**: `replay_exhausted` requeues
  every exhausted delivery of one subscription (newest first, capped 500/
  call; repeat to drain a backlog) for operator recovery after an endpoint
  outage — skips originals whose prior replay is in flight OR already
  succeeded (one query, never duplicates), refuses inactive subs, uniform
  404 cross-org. `POST /webhooks/{id}/replay-exhausted`, audited
  (`intg.delivery.bulk_replayed`). Diagnosed+cleared accumulated real-
  Postgres debt from repeated e2e runs (2554 pending outbox, 2589 subs)
  that had been breaking the global-`_drain` events suite.

- **R154 (third window)**: SCIM ServiceProviderConfig's advertised
  `bulk.maxOperations` now reads the same constant `apply_bulk` enforces —
  the two can no longer drift.

- **R153 (third window)**: the error report's last column is now a
  kind-appropriate `identifier` (email for users/roster, title for
  opportunities) instead of a users-only email column — still
  formula-injection-sanitized. Known limitation (documented, accepted):
  opportunities idempotency is best-effort — no unique index on
  (org, lower(title)) exists because the interactive API legitimately
  allows same-title postings, so two CONCURRENT imports of the same new
  title can land two drafts (a human reviews drafts before publish).

- **R151-R152 (third window, UI polish with teeth)**: job list rows show
  the template kind; uploads carry a mount-salted deterministic
  idempotency key (double-click lands on the SAME job instead of a
  duplicate, while a fresh page visit can legitimately re-import the
  identical file after fixing the environment).

- **R148-R149 (third window)**: import kind registry consistency invariant
  (IMPORT_KINDS == TEMPLATE_VERSIONS == KIND_SPECS, required ⊆ known);
  export-stream UI gains an optional explicit fields input so the R130
  `data.<key>` per-key selection is reachable from the admin surface
  (comma-separated, trimmed, empty = safe default allowlist).

- **R147 (third window, audit inverse check)**: same pattern for the audit
  trail — every `record_fabric_audit` call site is scanned and its action
  literal must be in AUDIT_ACTIONS (record_audit swallows unregistered
  actions silently, the R100 trap), so a typo'd audit can never ship as a
  silent no-op.

- **R146 (third window, catalog inverse check)**: the catalog test now
  scans every `emit_event` call site in app code and asserts its type is
  advertised (canonical or internal) — a new emission can no longer ship
  undiscoverable. The check immediately caught a REAL gap:
  `integration.sync.completed` was emitted but absent from the catalog —
  added to the alertable internals.

- **R143 (third window, mesh completeness)**: commit of a bulk import now
  emits `com.openskill.org.import.committed.v1` (counts only — never the
  roster) so SIS/HRIS webhook subscribers can react to bulk provisioning;
  catalog lists it among direct emissions; test asserts the event row,
  its subject (job id) and the absence of any email in the payload.

- **R141-R142 (third window, UI + live walk)**: data-page vitest coverage
  for the kind selector / per-kind header-map fields / JSON accept; live
  E2E extended with a REAL multipart JSON import walk (upload previews,
  commit creates, idempotent re-upload skips, unknown kind 422) — E2E now
  61/61 (was 49): R144 adds a live roster walk (cohort over HTTP, CSV
  roster import enrolls the member); R145 adds the opportunities walk —
  without an employer profile every row errors, after registering the
  profile the JSON import lands a draft-only posting.

- **R140 (third window, probe over R134-R138)**: 7 targeted mutants —
  retention status set, cutoff direction, blanked-job rescan, delete-failure
  blanking, PKCE challenge derivation, verifier persistence, unregistered
  audit action — all KILLED on first run; the new governance/PKCE/audit
  code is fully pinned by its tests.

- **R139 + final checkpoint (marathon3 close)**: connector contract tests
  rebuild fresh instances (the module-level CONNECTORS singleton is
  swapped by many tests — order pollution surfaced only in full-suite
  order). Final verification after R140-R151: fabric suite 264/264,
  cross-cutting consumers (controlplane/billing/webhooks) 618/618 plus
  employer 54 and cohort 45, web 764/764 + type-check + lint, live E2E
  61/61 (requires APP_ENV=test + EGRESS_ALLOW_PRIVATE=true in BOTH the
  API and the e2e process — the outbox is driven in-process; a crashed
  e2e run can leave a committed pending domain, hence the R150 tolerant
  sweep assert + e2e domain cleanup).

- **R138 (third window, Part O gap)**: bulk imports — mass account
  provisioning, exactly what auditors ask about — were the one admin
  mutation WITHOUT an audit trail. `intg.import.created` (kind/mode/
  dry_stats) and `intg.import.committed` (status/stats) now land in the
  append-only trail with the acting user; actions registered in
  AUDIT_ACTIONS (the R100 silent-swallow lesson), test asserts rows LAND.

- **R137 (third window, properties)**: hypothesis coverage over the new
  parse surface — detect_format and both parsers total over arbitrary
  bytes for all three kinds; CSV/JSON format PARITY (same logical rows
  validate to the same multiset, 400 examples). Writing the parity
  property exposed a real asymmetry — the CSV path strips every cell but
  JSON values kept whitespace — fixed by stripping in `_canon_obj`.

- **R136 (third window, race)**: TRUE-concurrency test over the new
  roster apply path — two different jobs, same (user, cohort) pair,
  committed via two real sessions: exactly one membership lands, the
  loser's row fails inside its savepoint (no poisoned session, no 500),
  both jobs reach a terminal status. Confirms the add-inside-savepoint
  discipline held for R129 code. 3x stable.

- **R135 (third window, RFC 9700)**: OIDC login now sends PKCE S256 —
  per-state `code_verifier` (intg14 column, nullable for legacy rows)
  minted at authorize, `code_challenge`+method on the redirect, verifier
  replayed at token exchange — so an intercepted authorization code alone
  is useless even for this confidential client. IdPs without PKCE support
  ignore the extra params (RFC 6749 requires ignoring unknowns).

- **R134 (third window, PII governance)**: uploaded import FILES (full
  rosters — emails, names) no longer sit in object storage forever:
  `sweep_import_files` deletes the stored object for terminal jobs older
  than 90 days and blanks `file_key` (idempotent; non-terminal jobs keep
  their file until committed/failed; a failing delete skips that job and
  retries next night). Wired into the nightly `_intg_retention_sweep`
  with an injected S3 deleter.

- **R133 (third window, mutation probe over R128-R131)**: 12 targeted
  mutants over the new parse/apply/export code — 10 killed outright; the 2
  survivors (roster default-role flip, in-file dup check disabled) were
  REAL coverage gaps, closed with a killer test (omitted role -> LEARNER,
  duplicate pair -> one membership + duplicate_in_file row error). 12/12
  killed on re-probe.

- **R131 (third window, Part K deferred kind)**: `opportunities` import
  template — employer migrations land postings as DRAFTS only (a human
  publishes; import can never reach candidates), gated on an existing
  EmployerProfile (every row errors `employer_profile_missing` otherwise),
  validated against OPPORTUNITY_TYPES / location modes / openings 1-999,
  idempotent by lower(title) per org. Third KIND_SPECS entry — CSV and
  JSON both serve it with header_map support.

- **R130 (third window, deferred item)**: per-key warehouse export of the
  events `data` payload via explicit `data.<key>` allowlist entries (events
  dataset only, max 20, same hash/drop anonymize; create+update share one
  `_check_fields` validator). The projection stays allowlist-BUILT, so
  unselected payload keys structurally cannot leak and the whole `data`
  field is still refused at config time.

- **R129 (third window, Part K deferred kind)**: `roster` import template
  shipped (was explicitly deferred at R19): email + cohort_slug (+ role
  learner|instructor) enrolls existing active org members into cohorts;
  per-kind `KIND_SPECS` (required columns, header_map keys, row validator)
  so CSV/JSON parsers serve both kinds; preview resolves cohort/user and
  reports cohort_not_found / user_not_in_org as row errors; commit skips
  existing members and never changes their role (human decisions win);
  atomic failures roll the whole transaction back at the request boundary.

- **R127-R128 (third window, Part K closure)**: CSV parser robustness
  suite (BOM/CRLF/quoted-newline/wide rows), then the JSON template Part K
  promised: shared `_validate_user_rows` extracted from the CSV path,
  `parse_users_json` (top-level array or `{"users": [...]}`, same email/
  NUL/role/dup rules, header_map support), `detect_format` content sniffing
  so create_job/commit dispatch with no API contract change; upload storage
  key + ContentType follow the sniffed format.

- **R120-R126 (third window, breadth+SDK)**: generic CRM read connector
  (Part E), full canonical-model list in the sync UI, mapping preview/run
  parity (Part H), bidirectional-profile rejection (was silent pull-only),
  connector-SDK boundary contract test (Part M). Fabric suite 246; E2E 49;
  web 762.

- **R97-R114 (third window, hardening)**: opt-in typed-model staging gate
  (R99); Part O completion — audit trail for 16 admin mutations (R100,
  record_audit has a registered-action allowlist the best-effort wrapper
  was silently swallowing), redirect URIs pinned to public_base_url not the
  Host header (R101/R102), least-privilege scope guard (R104), Part O
  checklist §20b; property-based tests over the pure cores (R107); and
  TRUE-concurrency race tests (R108-R113, two real sessions via gather)
  that found THREE production 500s the single-threaded probes had marked
  'unreachable': `db.add(x)` before `begin_nested()` leaves a pending
  INSERT that replays at the next flush and poisons the session on a
  unique-violation loser — fixed in identity._link, lti.ensure_tool_key,
  and domains.verify()/sweep_pending. Fabric suite now 232 tests incl.
  races + properties.

- **R86-R96 (third window)**: connector rate-limit handling (capped
  Retry-After + bounded transient-5xx retry — Part G); LTI Dynamic
  Registration 1.0 (paste the platform config URL, everything negotiated;
  plain-OIDC refusal + per-endpoint egress screens); SAML Single Logout
  (IdP-initiated Redirect binding, SIGNED-only — logout-CSRF refused,
  signed string rebuilt from RAW query segments because parse_qs plus-
  decoding corrupts base64 signatures; a signed LogoutResponse carrying a
  NameID is refused by the root-tag check) + SLO URL metadata capture
  (intg11) + SP-metadata advertisement; attribute-map editor UI; SCIM
  lifecycle event feed completed (reactivation arms); import header-alias
  column mapping persisted on the job (intg12, commit re-parses with the
  SAME map); event-type catalog endpoint + subscription datalist (self-
  consistency test: every advertised pattern passes the create validator);
  byte-exact delivery payload archive (intg13 — retries/replays resend the
  archive even if the event row mutates) + inspection endpoint. Parquet
  export deferred deliberately (pyarrow dependency decision). Live E2E
  49/49; fabric suite 217 tests.

- **Final verification (marathon2 close)**: backend 7248/7248 green
  (chunked after two OOM-killed monolithic runs; the 52 transient 429s in
  the talent chunk were execution-compression artifacts of the in-process
  sliding-window limiter — green with a per-test reset shim, untouched by
  this branch); web 762/762 + tsc clean; live-HTTP E2E 47/47.

- **R77-R85 (admin-surface CRUD completion)**: webhook subscription PATCH
  (edit without secret churn + re-enable), SCIM filter operator case-
  insensitivity (RFC 7644), SCIM Group PUT (Okta group-push dialect,
  full member-set replace through the shared delta engine; also /Bulk-
  dispatchable), pagination edge pins, export-stream PATCH (edit/disable)
  - sync-profile PATCH (schedule/policy; mapping stays pinned until an
    explicit repin — §10.1), import-job history endpoint + UI, and DELETE
    endpoints with guard semantics (live-run 409, mapping-in-use 409,
    cascade semantics documented per resource). Live E2E grown to 44 checks
    incl. the SSO browser journey and expanded IDOR walls.

- **R63-R71 (login-journey closure)**: sub-page breadcrumbs; operations
  guide (docs/ops/integration-fabric-operations.md); acceptance-criteria
  mapping (§20a); and a manual end-to-end walk of the BROWSER login
  journey that found three production-dead paths no API test could see —
  R67 discovery handed SAML orgs the OIDC authorize URL, R69 the ACS/
  callback redirect targeted /auth/sso-complete which never existed
  ((auth) is a route group: no URL segment — every prod SSO login 404'd
  with tokens stranded in the fragment; new /sso-complete page consumes
  the fragment, scrubs the hash, hydrates via /auth/me), R70 the state
  row's redirect_to was written but never read (deep links lost; now
  round-trips behind open-redirect guards on both sides), R71 enforced-
  SSO password logins now hand off into the SSO flow instead of a dead
  error, R68 the login page gained the missing SSO entry entirely.

- **R55-R62**: e2e-caught /Bulk serialization crash (exc.body unbound
  method — unit test never serialized; now json.dumps the envelope);
  probe campaign over every NEW module (apply_bulk incl. SAVEPOINT
  isolation proof, NRPS incl. malicious rel=next egress refusal + page
  cap, metadata refresh, back-channel logout, retention batching,
  connection-health sweep, gradeable hook org-scoping, generic REST/ATS
  connectors — which had ZERO direct tests), outbox-handler sync path
  driven end-to-end; failed-attempt response snippets (intg10, Svix
  parity). Live E2E now 39 checks.

- **R49-R54 (second window, continued)**: LTI NRPS v2 membership
  pre-provisioning (launch captures namesroleservice; paginated fetch via
  generalized service_token; identity-resolution ladder, instructor/student
  ceiling) + LTI admin UI with one-click roster sync; SAML metadata
  auto-refresh (daily + manual, hardened parse, signing-keys only,
  pem-diff rotation detection) driving the formerly never-driven
  idp_metadata_url column; SCIM /Bulk (100 ops, per-op SAVEPOINT,
  failOnErrors, bulkId refs 501); immediate-rotation UI action.

- **R35-R47 (second marathon window)**: fabric health summary endpoint +
  hub status strip (R36); webhook test-send, Svix parity (R37); connection
  health sweep cron with unhealthy-transition alerts (R41); OIDC
  Back-Channel Logout 1.0 (R42); nightly retention sweep (R44); per-
  subscription delivery stats (R46). Probe campaign extended to the LTI
  launch validator, bulk import, roster provisioning, AGS score push,
  warehouse projection (narrowed-allowlist leak + org-salt joinability
  killers), connections PATCH-path SSRF screen, OneRoster connector
  pagination (<= mutant silently dropped page 2+), sso_admin screens, the
  events API layer org filters, and cron registration (guard test pins all
  7 sweeps). Live E2E extended to 37 checks — all passing.

- **R20-R33 (marathon hardening, continued)**: R20 reversible identity
  unlink (list/DELETE, uniform 404) + webhook-subscription management UI;
  R21 org-page nav entry + per-route rate limits on every protocol surface
  (SCIM had none); R22 sync-conflict adjudication (accept_theirs/keep_ours/
  dismiss drives resolved_by/resolved_action; both sides stored in detail);
  R23 stale-adjudication 409 guard + identity-links UI; R24 expandable
  CloudEvent payloads; R25 non-vacuous rate-limit route guard test;
  R26-R33 mutation probes over every money/security core — mapping
  evaluator (17 holes closed), SSRF guard (mixed-resolution refusal,
  IPv4-mapped v6, classification matrix), event mesh (internal-wildcard
  feedback-loop guard), identity resolution (7 takeover killers incl.
  two-members-same-email and suspended-link hot path), OIDC (expired
  state, require-exp, email_verified=false), SCIM (group_map admin/owner
  escalation 422, PUT deactivation, reactivation), sync engine (backfill
  cursor reset, claim/terminal guards, requeue resumes from own cursor).
  Surviving mutants individually verified equivalent or defense-in-depth.
- **R19**: SAML cert-expiry sweep (30-day window, daily-deduped mesh alert,
  06:18 cron); ADR deferred-items audit. **R18**: SCIM group-map editor UI.
- **R17**: deep-linking response signing (tool-key JWT; opaque `data`
  round-trip) + select endpoint; hub Upgrade button.
- **R16**: scheduled EXPORTS were never driven (same gap class as R11's
  scheduled syncs) — sweep + nightly cron (02:47).
- **R15**: live-API E2E lifecycle (tests/e2e_integration_lifecycle.py, 32
  checks incl. a local signed-webhook sink). E2E-caught: (1) the webhook
  REQUEST SCHEMA duplicated the event-type check and missed R7's mesh arm —
  the live API rejected com.openskill.* subscriptions service tests
  accepted; (2) the legacy subscription URL screen ignored the boot-guarded
  EGRESS_ALLOW_PRIVATE flag. Lesson re-learned: layer-duplicated validation
  drifts — share the predicate.
- **R14**: legacy rotate-secret swapped keys in place and hard-broke
  receivers mid-window — now co-signs for 7 days (?immediate=true for the
  leaked-key path); duplicate P2 rotate endpoint removed. Mapping editor +
  preview UI.
- **R13**: explicit provider-version upgrade endpoint (re-validate config
  against the new schema; pin never bumps silently). SAML create UI.
- **R12 (P3b)**: SAML SP via signxml. XSW-safe by construction (only the
  signed subtree is consumed); exclusive-c14n requirement pinned by test;
  per-connection cert pinning; assertion-id replay cache; unsolicited
  responses rejected.
- **R11**: pending-domain DNS cron, scheduled-sync sweep (the `schedule`
  column was never driven), stale-run reaper cron; authed error-report
  download in the UI (bare <a href> 401'd).
- **R10 (P11)**: five admin pages (hub/identity/sync/events/data) + tests.
- **R9**: §18 acceptance chain as one inline test (SCIM → SSO → roster →
  cohort → event → signed delivery → AGS → export → deprovision sweep).
- **R8 (P10)**: consent-gated ATS push (ids+pipeline only; consent_missing
  conflicts; last_outbound change detection); invoice.finalized routed to
  tenant orgs as a privacy-safe id-only notification.
- **R7**: adversarial sweep, 9 defects — mapping-doc size cap; SCIM strict
  email; junk claim types; disabled-provider runs; concurrent import
  commits; unscheduled reaper; mesh events unsubscribable via API; SCIM
  group-rename 500; login-state rows never purged.
- **P1–P6/P7 (earlier same branch)**: fabric core, event mesh + wiring,
  OIDC SSO + identity resolution + enforce-SSO/break-glass, SCIM server,
  mapping + sync engine (destination-confirmed cursors; the JSONB
  identity-assignment bug — re-assigning a mutated dict skips the UPDATE —
  cost one debugging round), roster provisioning, OneRoster connector,
  LTI launch + AGS, bulk import, warehouse export.

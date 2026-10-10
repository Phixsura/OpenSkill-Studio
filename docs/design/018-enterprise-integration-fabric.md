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
refresh; rotated refresh tokens overwrite previous ciphertext in the same txn; a
refresh failure with `invalid_grant` moves the connection to `error` and emits
`integration.connection.errored`. API never returns credential material — the
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
fabric-internal `integration.connection.errored, integration.sync.completed,
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

# Issue #43 World-Class Research — Enterprise Integration Fabric

Research survey of world-class products, protocols and open-source systems relevant to
issue #43 (SSO/SCIM, SIS/LMS/HRIS/CRM connectors, event mesh, governed data sync).
Feeds the ADR for the Enterprise Integration Fabric. Organized as 8 streams mapped to
issue parts A–O.

| Stream                         | Issue parts | Systems studied                                                       |
| ------------------------------ | ----------- | --------------------------------------------------------------------- |
| 1. Enterprise SSO              | B           | WorkOS, Scalekit, Atlassian break-glass, pysaml2/python3-saml/authlib |
| 2. SCIM provisioning           | B           | RFC 7643/7644, Okta, Entra, scim2-models/scim2-server                 |
| 3. Education integrations      | C, J        | OneRoster 1.2, LTI 1.3 Advantage, Clever, ClassLink, Edlink           |
| 4. Unified APIs (HRIS/ATS/CRM) | A, D, E     | Merge.dev, Finch, Nango, Truto                                        |
| 5. Event mesh & webhooks       | F           | Svix, Standard Webhooks, CloudEvents, outbox pattern                  |
| 6. Sync engine                 | G           | Airbyte protocol, HubSpot↔Salesforce sync, hotglue                    |
| 7. Mapping & connector SDK     | H, M        | JSONata/JMESPath, Prismatic, Airbyte CDK                              |
| 8. Governance & security       | I, K, L, O  | SSRF defense, account linking, bulk import, Stripe Data Pipeline      |

## What already exists in this codebase (build on, don't duplicate)

- `app/models/webhook.py` — `WebhookSubscription` (org-scoped, `events` JSONB array,
  per-subscription `secret`, `active` flag). No delivery log, retry, signing scheme,
  or DLQ yet: the event-mesh work extends this.
- Outbox pattern already in production use (`app/ecosystem/worker.py`,
  `app/experiments/worker.py`) — drivable inline in tests.
- `app/core/crypto.py` — encrypted write-only credentials, already used by
  `provider.py` (R-series hardened: write-only responses, capability re-checks).
- Org multitenancy (`require_org_member`), Cohort/ClientBrief/Talent/Passport models,
  consent-scoped candidate sharing (ADR-015), points/cert idempotency patterns.

---

# Stream 1 — Enterprise SSO (SAML 2.0 / OIDC, multi-tenant)

## 1.1 WorkOS connection model (the industry-reference shape)

WorkOS is organization-centric: an **Organization** represents the customer tenant; an
**SSO Connection** is one IdP integration (SAML or OIDC) belonging to that organization.
The connection answers _"how does this person prove who they are"_, never _"should this
person have access"_ — authorization stays in the app.

Key mechanics worth copying:

- **Initiation**: SSO is initiated with an `organization` parameter (preferred) or a
  `connection` id. Multi-tenant apps keep a single redirect URI.
- **Domain verification anchors everything.** An `organization_domain` object carries a
  `verification_token` the admin sets as a DNS TXT record; WorkOS polls until found.
  Only one organization may hold a given verified domain per environment (prevents
  collisions and domain-claim squatting). JIT provisioning and IdP routing key off the
  _verified_ domain only.
- **Metadata exchange is bidirectional**: SP side provides ACS URL + SP Entity ID;
  customer provides IdP metadata URL (SAML) or client id/secret + discovery URL (OIDC).
- **Admin Portal pattern**: a self-serve, guided setup UI for the customer's IT admin
  (configure IdP, verify domain, test connection before go-live) removes the #1
  onboarding support burden.
- **Tenant policy flags**: "SSO required", "MFA required", with explicit carve-outs for
  guests/contractors who don't match the verified domain.
- Users signing in via SSO under a verified domain skip email verification.

Sources: [WorkOS SSO docs](https://workos.com/docs/sso),
[domain verification API](https://workos.com/docs/domain-verification/api),
[organization access model](https://workos.com/blog/how-workos-decides-organization-access).

## 1.2 SAML hardening checklist (distilled from WorkOS/Scalekit/LoginRadius guides)

1. **Never accept unsigned SAML.** Require signed responses _and_ assertions; enforce
   SHA-256+, reject SHA-1. Validate the signature **reference URI** exactly — XML
   signature wrapping (XSW) works precisely when a verifier checks "a valid signature
   exists somewhere" while consuming attributes from an unsigned clone element.
   Canonicalize before verification; use a maintained XML library hardened against XXE.
2. **Pin the certificate to the connection, not globally.** A certificate trusted
   across tenants means one compromised customer IdP can mint assertions accepted by
   every other tenant. Enterprise security reviews explicitly test this.
3. **Audience + entity isolation.** Unique SP Entity ID per environment; exact audience
   matching; prod and staging never share identifiers.
4. **Replay protection**: cache assertion IDs until their `NotOnOrAfter`, reject
   duplicates. `RelayState` must validate against an allowlist of redirect targets.
5. **Certificate rotation must be overlap-tolerant**: accept multiple concurrent
   signing certs per connection; periodically re-fetch the IdP metadata URL (IdPs
   publish both active and next certificates during rotation windows); alert a named IT
   contact at 90/30/7 days before expiry. Keep signing vs encryption cert roles
   distinct.
6. **Single Logout** for session cleanup; TLS 1.2+ on all SP endpoints.

## 1.3 Enforced SSO + break-glass (Atlassian model)

- A **break-glass account** is a dedicated admin account that bypasses SSO, governed by
  an immutable auth policy: static password + hardware MFA (WebAuthn), _not_ integrated
  with the IdP, scope restricted to the admin interface only.
- Alternative: one-time recovery codes — a break-glass request spends a single-use code
  and writes an audit entry with IP + user agent.
- Operational rule: **before** starting a cert rotation, confirm the break-glass path
  still works; close the change only after all connections verified, not after one
  admin logs in.

## 1.4 Python implementation landscape

- **SAML SP**: `pysaml2` (pure Python, SP+IdP, WSGI-era but adaptable; Python 3.13
  compat issues reported) vs `python3-saml` (SP-focused, lxml-based). Both are
  DIY-heavy for multi-tenancy — per-tenant cert pinning and signature validation is on
  us either way. Realistic estimate from vendor comparisons: 1–2 weeks for the direct
  integration, plus the hardening list above.
- **OIDC RP**: `authlib` is the standard choice and fits the existing FastAPI stack.
- Hosted brokers (WorkOS et al.) expose SAML as an OIDC interface — the architecture to
  emulate internally: one OIDC-shaped callback path; SAML handled in an isolated module
  that normalizes to the same internal "verified external identity" struct.
- **Session gotcha**: an active JWT session outlives IdP removal — deprovisioning
  (SCIM, Stream 2) must revoke sessions, not just block new logins. This matches the
  existing R88-class rule: every hard-revoke path sweeps rotation predecessors.

---

# Stream 2 — SCIM 2.0 provisioning

## 2.1 Protocol surface (RFC 7643 schema, RFC 7644 protocol)

Minimum conformant server: bearer-token auth + `/Users` and `/Groups` with GET, POST,
PUT, PATCH, DELETE, plus discovery endpoints `/ServiceProviderConfig`,
`/ResourceTypes`, `/Schemas`. Pagination via `count`/`startIndex` on list responses;
`ListResponse` envelope is returned even for zero results.

## 2.2 The rules every real-world implementation learns the hard way

- **Soft delete, never hard delete.** `active: false` _is_ deprovisioning
  (RFC 7643 §4.1.1). Keep the record ≥30–90 days (HR-error window), preserve
  referential integrity (owned records, audit entries). An IETF draft
  (`draft-ansari-scim-soft-delete`) adds `isSoftDeleted`; useful semantics: DELETE on
  an already-soft-deleted resource → 404; a create reusing a soft-deleted `userName`
  does **not** 409.
- **PATCH-deactivate ≡ DELETE.** Entra deprovisions via
  `PATCH {"op":"Replace","path":"active","value":false}` — never calls DELETE. Okta
  likewise never DELETEs users. Both handlers must run the same logic **including
  immediate session/token revocation**.
- **Parse deactivation leniently**: accept `"value": "False"` as a quoted string,
  `"Replace"` with capital R, fully-qualified attribute URNs in paths; compare ops
  case-insensitively.
- **PATCH is SCIM PatchOp** (`urn:ietf:params:scim:api:messages:2.0:PatchOp`), not JSON
  Patch. Invalid ops reject the _entire_ request (no partial application); success
  returns 200 + full updated resource.
- **Group membership = deltas in a transaction.** The classic failure: IdP sends a
  2,000-member full replace, request times out halfway, group has 1,200 members and no
  log. Apply `op: add/remove` on `members` incrementally; wrap in one transaction.
  Okta removes members via filtered paths: `members[value eq "..."]`.
- **Duplicate create → 409 + `scimType: "uniqueness"`** so the IdP fetches and links
  the existing record. IdPs retry constantly; everything must be idempotent.
- **Existence-check filter** `GET /Users?filter=userName eq "x"` is mandatory in
  practice; map `externalId` → internal id so updates/deletes resolve.
- **Rate limiting**: 429 + `Retry-After` is explicitly allowed (RFC 7644 §3.7) — wire
  it before a production resync, not after.
- **Logging**: operation, requestor, status, connection id, timestamp — never full
  payloads (PII) or tokens; error bodies stay SCIM-shaped, never stack traces. Keep the
  exact received message id so "why did this person lose access" is answerable.

## 2.3 Python ecosystem

[`scim2-models`](https://github.com/python-scim/scim2-models) (Yaal Coop): Pydantic-2
models for RFC 7643/7644 payloads — parsing, validation, context-aware serialization;
Python 3.10–3.14. Companion [`scim2-server`](https://github.com/python-scim/scim2-server)
is an in-memory reference (ETags, PATCH, filtering — no Bulk), and `scim2-tester` is a
compliance test harness we can run in CI. Filter parsing:
[`scim2-filter-parser`](https://pypi.org/project/scim2-filter-parser/) (15Five)
transpiles SCIM filters to SQL via an attribute map — widely used (~533K weekly
downloads) but maintenance-inactive; wrap it or vendor the small core.

Recommendation: adopt `scim2-models` for payload handling, write our own thin router
(it must integrate org scoping, outbox events and session revocation anyway), run
`scim2-tester` in CI against the test app.

---

# Stream 3 — Education integrations (SIS/LMS)

## 3.1 The broker landscape and who is source of truth

The **SIS is the source of truth** (PowerSchool, Infinite Campus, Skyward): demographics,
enrollment, schedules. Brokers sit between SIS and apps:

- **Clever** — Secure Sync pulls from the SIS nightly and pushes rosters to connected
  apps; free for districts, vendors pay. District admins set **data-sharing rules**
  (which users/classes/grade levels each app sees); the district-app token only reaches
  scoped users. LMS Connect layers LTI (grade passback, LTI SSO) on top of Secure Sync.
- **ClassLink** — districts pay; vendors get roster data free via **open OneRoster**.
  Roster Server is installed by the district and exposes OneRoster endpoints.
- **Edlink** — aggregator on top of brokers; useful cautionary notes: refuses Clever
  Secure Sync as a _secondary_ enrichment source, doesn't support extended models.
- Operational pattern from production sync processors: **per-district isolation** — a
  problem in one district skips only that district in the nightly run (150K-user
  districts exist); dirty SIS data is an expected precondition, so conflict/quality
  reporting is a feature, not an edge case.

## 3.2 OneRoster 1.2 (1EdTech)

- Three services: **Rostering**, **Resources**, **Gradebook**; CSV _and_ REST bindings.
  REST base path `/ims/oneroster/rostering/v1p2` (changed from v1p1).
- Rostering REST is **read-only for the consumer** — the app pulls; there is no push.
  Gradebook in 1.2 has both push and pull endpoints.
- Canonical entities: orgs, academic sessions (terms), courses, classes, users
  (`preferredName` added in 1.2), enrollments, demographics.
- Security: OAuth 2.0 client-credentials with scopes like
  `https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly`.
- Filtering: logical query params, recommended max one AND/OR per filter.
- Conformance requires supporting at least one service mode; certification exists —
  design canonical roster objects so a OneRoster connector is a _mapping_, not a schema
  change.

Spec: [OneRoster v1.2](https://www.imsglobal.org/spec/oneroster/v1p2) and the
[Rostering REST binding](https://www.imsglobal.org/sites/default/files/spec/oneroster/v1p2/rostering-restbinding/OneRosterv1p2RosteringService_RESTBindv1p0.html).

## 3.3 LTI 1.3 / LTI Advantage

Core launch + three services = Advantage:

- **Deep Linking 2.0** — instructor picks specific tool content from inside the LMS; it
  lands as a real course item.
- **AGS 2.0** (Assignment & Grade Services) — line items, numeric scores + comments back
  to the LMS gradebook, activity/completion status, instructor override with history.
- **NRPS 2.0** — course roster/enrollment shared with the tool at launch scope.

Launch flow (OIDC third-party-initiated), with the validation set that distinguishes a
safe implementation:

1. LMS → tool login-initiation URL with `iss`, `login_hint`, `target_link_uri`,
   `lti_message_hint`, `client_id`.
2. Tool → LMS auth endpoint: `response_type=id_token`, `response_mode=form_post`,
   `scope=openid`, `prompt=none`, + `state`, `nonce`, `lti_deployment_id`.
3. LMS POSTs signed `id_token` + `state` to the tool launch URL.

Tool-side validation on **every** launch: `iss` matches registered platform; `aud` (and
`azp` if present) equals client id; **`deployment_id` is in the registration's allowed
deployment list** (string compare — one registration can have many deployments);
signature verified against the platform JWKS; `state` single-use and session-bound;
`nonce` matches the session-stored value only (never honor a nonce request param — a
captured id_token reveals its nonce claim); `iat`/`exp` windows; LTI version claim
`1.3.0`; allowed message type.

**JWKS rotation**: if the id_token `kid` is not in the cached JWKS, re-fetch once and
retry, rate-limited (~30s floor). Library defaults are often wrong here (some only
retry against already-fetched keys).

Grade return is explicit and configurable per deployment — matches the issue's "grade
return should be explicit" requirement directly.

Sources: [LTI Advantage overview](https://www.imsglobal.org/lti-advantage-overview),
[OIDC launch walkthrough](https://andyfmiller.com/2018/12/28/launching-an-lti-1-3-resource-link-using-openid-connect-third-party-login/),
[Canvas id_token anatomy](https://cbennell.com/posts/whats-in-a-canvas-lms-lti-1-3-jwt/).

---

# Stream 4 — Unified-API platforms (HRIS / ATS / CRM)

## 4.1 Merge.dev — the common-model playbook

- One normalized schema per category (HRIS, ATS, CRM, accounting, …); the app
  integrates against `Employee`/`Candidate`/`Contact`/`Opportunity` common models and
  every provider maps into them. 220+ integrations ride on this.
- **Sync-and-store architecture**: Merge syncs provider data into its own store and
  increments on it, enabling frequent resyncs within provider rate limits. (Trade-off
  flagged by competitors: customer data retained indefinitely until deleted.)
- The common model deliberately contains only fields _most_ providers expose. Four
  escape hatches, in increasing rawness:
  1. **Field Mappings** — extend/override common-model fields, mapped from provider
     fields using **JMESPath** expressions, with _field coverage percentages_ and
     _preview values_ in the mapping UI;
  2. **Remote Field Classes** — read/write non-mapped data in a standardized wrapper;
  3. **Remote Data** — original raw provider payload via query param;
  4. **Authenticated Passthrough** — raw request with stored credentials (caller owns
     pagination/retries/rate limits).
- **Finch** (employment-only) wins on payroll depth (pay-statement level earnings/
  taxes/deductions, deduction write-back) — a reminder that category depth and breadth
  trade off; our canonical models should capture the fields _our_ flows need, with
  passthrough-style raw retention for the rest.

Sources: [Merge common models](https://www.merge.dev/features/common-models),
[supplemental data docs](https://docs.merge.dev/merge-unified/supplemental-data/overview),
[Finch comparison](https://www.merge.dev/blog/finch-api-alternatives).

## 4.2 Nango — the open-source reference implementation

([GitHub](https://github.com/NangoHQ/nango), Elastic License 2.0, self-hostable.)

- Three primitives: **Auth** (managed OAuth/API-key flows, encrypted token store),
  **Proxy** (inject credentials, retries, rate limits per request), **Functions**
  (TypeScript syncs/actions running on a Temporal-backed runtime with per-tenant
  isolation).
- All provider knowledge lives in one declarative **`providers.yaml`**: per provider —
  `auth_mode: OAUTH2`, authorization/token URLs, proxy `base_url`. Adding a provider is
  config, not code, for the auth/proxy layer.
- **Token refresh discipline**: a distributed lock prevents concurrent refreshes per
  connection; rotated refresh tokens are stored; provider-specific expiry quirks are
  encoded centrally.
- Connection flow: frontend opens a session-token'd connect UI → user authorizes →
  Nango stores credentials → **auth webhook with a `connection_id`** that the app
  persists against its own org/user. This `connection_id` indirection (app never
  touches tokens) matches our existing write-only credential rule.

## 4.3 Prismatic — connector SDK & versioning discipline

- TypeScript SDK (`@prismatic-io/spectral`); connector anatomy: `actions/`,
  `triggers/` (webhooks + HMAC validation), `connections.ts` (API key / OAuth2),
  `inputs.ts` (reusable typed fields), `client.ts`, `index.ts`.
- **Manifests = capability declaration**: each component publishes a manifest
  describing its connections, actions, triggers, data sources — a pointer to platform-
  registered capabilities, not the source code.
- **Versioning**: integer-incrementing versions per publish; **integrations never
  auto-upgrade** — each consumer pins a version and upgrades deliberately; publishing
  never auto-deploys to customers (each customer instance stays on its version until
  deliberately upgraded). CI/CD via CLI publish with git commit association.
- Customer configuration via JSON-Forms-driven wizards, deployable by non-dev teams.

The pin-and-deliberately-upgrade model is exactly the registry discipline this codebase
already applies to skill/workflow packs (ADR-009/010) — the connector SDK should reuse
that machinery, not invent parallel versioning.

---

# Stream 5 — Event mesh & webhook delivery

## 5.1 CloudEvents 1.0 (CNCF) — the envelope

Required attributes: `id` (unique per producer — **the idempotency key at every hop**),
`source` (URI of producing context), `specversion` (`1.0`), `type` (reverse-DNS,
e.g. `com.openskill.learner.enrolled`). Optional: `datacontenttype`, `dataschema`
(URI; **incompatible schema changes SHOULD change the URI**), `subject`, `time`
(RFC 3339).

Versioning conventions that work in practice:

- Version in the type name: `{domain}.{entity}.{action}.vN` — `type` is immutable once
  published; a breaking change mints a new type (or new major in `dataschema`).
- Treat the event as a versioned aggregate snapshot inside a stable envelope.
- Pair with the **outbox**: envelope rows written transactionally with the domain
  change; the transport (today: Postgres outbox worker → webhook dispatch; later: a
  broker) is a swap, not a rewrite. This codebase already has the outbox half.

Sources: [CloudEvents spec](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md),
[primer (versioning)](https://github.com/cloudevents/spec/blob/main/cloudevents/primer.md).

## 5.2 Svix / Standard Webhooks — delivery mechanics worth copying verbatim

- **Signature scheme** (basis of the [Standard Webhooks](https://www.standardwebhooks.com/) spec):
  headers `webhook-id`, `webhook-timestamp`, `webhook-signature`; signed content is
  `{id}.{timestamp}.{payload}`; HMAC-SHA256 with the base64-decoded portion of a
  `whsec_`-prefixed secret; signature header carries space-delimited `v1,<sig>` entries
  (any may match → **zero-downtime secret rotation**); reject timestamps >5 min off
  (replay guard); constant-time compare; verify the **raw body**, never re-serialized
  JSON.
- **Retry schedule**: 8 attempts — immediate, 5s, 5m, 30m, 2h, 5h, 10h, 10h (expo +
  jitter); receiver must respond within 15s; endpoint **auto-disabled after 5 days** of
  consistent failure.
- **Idempotency**: `webhook-id` constant across retries and _inside the signed
  content_ (unlike unsigned delivery-id schemes); receivers dedupe on it with ~24h TTL.
- **DLQ + replay**: exhausted deliveries are parked with payload, destination and the
  full attempt history (status codes/timeouts visible per attempt); replay via UI/API.
  Exhaustion itself emits an operational event (`message.attempt.exhausted`) — make
  delivery failure _alertable_, not just loggable.
- Known trade-offs: FIFO ordering is expensive (Svix caps ~20 msg/s when sequential);
  per-destination retry customization is rare — don't promise ordering.

## 5.3 Fit against the existing `WebhookSubscription`

The existing model has url/events/secret/active. The gap list (= work items):
delivery/attempt tables, Standard-Webhooks signing, retry scheduling on the existing
outbox worker, DLQ semantics, replay endpoint, auto-disable policy, and per-attempt
observability. The outbox already gives transactional publish.

---

# Stream 6 — Sync engine

## 6.1 Airbyte protocol — state, cursors, checkpoints (the canonical design)

- **State message contract**: a state may be given back to a source on the next run
  **only if it was emitted by the source _and_ echoed by the destination** — the
  destination echo confirms all records up to that point were committed. Records sent
  but not confirmed don't advance the cursor and are re-read next run (at-least-once).
- **Cursor**: a comparable field (commonly `updated_at`); records ≤ cursor are synced,
  > cursor are new. Sources may be `source_defined_cursor` with a
  > `default_cursor_field`. Emit state every N records (`state_checkpoint_interval`), not
  > only at stream end; Airbyte's SLO: **≤30 min of replay on failure**.
- **State granularity**: per-stream state (preferred), global, or legacy single-blob.
- **Sync modes**: `FULL_REFRESH` (always supported) and `INCREMENTAL`; destination
  sides: overwrite, append, and **append + deduped** (upsert semantics — modified rows
  merge into the latest version; with CDC this produces an SCD history table + deduped
  table).
- **Resumable full refresh**: parallel partitions, each state carries `partition_id` +
  incrementing `id`; the destination commits states in id order so checkpoints stay
  sequential despite out-of-order records.
- The issue's Part G checklist (cursor/checkpoint, idempotency, pagination, rate
  limits, retries, backfill, tombstones, conflict detection, partial failure, resume)
  is precisely the Airbyte protocol surface — adopt its vocabulary in `SyncRun`
  records: per-stream cursor state blob, checkpoint cadence, at-least-once + dedup key.

Sources: [Airbyte protocol](https://docs.airbyte.com/platform/understanding-airbyte/airbyte-protocol),
[resumability](https://docs.airbyte.com/platform/understanding-airbyte/resumability),
[sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes).

## 6.2 Bidirectional sync & conflicts (HubSpot↔Salesforce production lore)

A conflict = same field, same record, changed in both systems before either synced.
Strategies, in production-preference order:

1. **Field-level ownership** (the issue's "source-of-truth policy per field/entity"):
   each field has one authoritative system; non-overlapping edits both survive; a
   system cannot overwrite a field it doesn't own. HubSpot's native connector exposes
   exactly this per-field: _Two-Way (most recent wins)_ / _Always use X_ / _Prefer X
   unless blank_.
2. **Last-write-wins** as fallback for low-stakes fields only — dangerous with clock
   skew and with **echo writes** (the "winning" write being a reflection of the losing
   one).
3. **Manual review queue** for ambiguous/critical conflicts.

Hard-won rules:

- **Minimize bidirectional fields.** Default one-way; enable two-way per field only
  where truly needed. Decide ownership _before_ enabling sync.
- **Echo/loop suppression**: record `last_sync_source` per record; on inbound change,
  compare changed fields against our last outbound write — identical ⇒ echo ⇒ discard.
- **Semantic traps**: fields with directional semantics (HubSpot `lifecyclestage` only
  moves forward) must be owned, never blind-LWW.

---

# Stream 7 — Declarative mapping & connector SDK boundary

## 7.1 Mapping language choice (Part H: "bounded, no arbitrary code")

- **JSONata** — declarative, sandboxed JSON query+transform (XPath 3.1 lineage);
  Turing-complete, which cuts both ways: expressive enough for real mappings, needs
  evaluator limits (depth/time) when exposed to tenants. Used by Truto for custom-object
  mapping.
- **JMESPath** — simpler, standardized (AWS CLI), extraction + reshaping + functions;
  _not_ Turing-complete — easier to bound. **Merge uses JMESPath for its Field
  Mappings product**, paired with field-coverage % and preview values.
- Design pattern from LinkedIn QDAG: a small **macro surface embedded in YAML/JSON that
  compiles down to a known-safe expression language** — the mapping _document_ is
  structured config (per-field: source path, transform chain, enum map, default,
  reference lookup), and only leaf expressions use the expression language.

Recommendation: a structured `MappingProfile` JSONB document (declared fields, enum
maps, defaults, reference lookups as first-class config) with **JMESPath for leaf
extraction only**, Python-side evaluation with input-size/recursion caps, and a
**mapping preview endpoint** that runs the profile against sample records
(Merge/MapForce-style preview is the UX bar). No eval of tenant code — this also keeps
the R83-class "no code execution from manifests" invariant.

## 7.2 Connector SDK boundary (Part M)

Synthesis of Prismatic manifests + Nango providers.yaml + Airbyte's spec/discover:

- A connector declares, as **versioned data**: auth scheme(s), capabilities (which
  canonical streams it can read/write, which operations), endpoints/base URLs, webhook
  trigger definitions with signature validation params, and config schema (JSON-Schema
  for the setup wizard).
- Core services consume only the declaration + canonical models; connector
  implementations register against the declared capabilities. Capability declarations
  are **permission-scoped and versioned**; consumers pin versions; no auto-upgrade.
- This mirrors ADR-011's provider-capability abstraction and the R83 rule
  (per-step `requires_capabilities` as feature sets, runtime re-check at binding) —
  extend that machinery to connectors rather than a second system.

---

# Stream 8 — Governance & security

## 8.1 SSRF-safe outbound traffic (Part O; applies to webhooks _and_ connectors)

Webhook SSRF is harder than classic SSRF: validation must hold **at every delivery,
including retries hours later** — a URL public at registration can point at
127.0.0.1 via DNS rebinding before the next retry (attacker controls TTL).

Control set (priority-ordered):

1. **Centralized egress client** — one hardened HTTP client for _all_ outbound traffic
   (webhooks, connector calls, metadata fetches) enforcing the policy; lint/review rule
   forbidding direct httpx/aiohttp use outside the egress module.
2. **Validate the resolved IP, not the URL string**; block 127/8, 10/8, 172.16/12,
   192.168/16, 169.254/16, ::1, fc00::/7, fe80::/10, IPv4-mapped IPv6, decimal/octal
   encodings.
3. **Pin the connection**: resolve once → validate IP → dial that exact IP with the
   Host header set to the hostname. No re-resolution between validation and connect ⇒
   rebinding window eliminated. Re-validate on **every dispatch**, not registration.
4. **Schemes http/https only; redirects disabled** (or re-validated per hop).
5. Response size + timeout caps; never echo raw upstream responses to clients.
6. Webhook "test" buttons only fire real validated events — never an unvalidated
   configuration-time fetch.
7. Defense in depth at network layer where deployed (egress deny, IMDSv2).

## 8.2 Identity resolution & account linking (Part I)

- **Naive email matching is the top vulnerability**: providers differ in email
  verification assurance; linking logic that trusts the email claim enables takeover
  without breaking OAuth at all.
- Rules: **only verified emails participate in matching**; email/UPN/
  `preferred_username` changes never re-link or merge — link on the IdP's **stable
  subject identifier** captured at first login; ambiguous matches require **explicit
  admin confirmation** (the issue says this too); prefer **linking** (reversible,
  auditable) over merging (irreversible).
- Race safety: case-insensitive unique constraint + single-transaction upsert, not
  SELECT-then-INSERT; provisioning callbacks idempotent and restartable without
  creating duplicates.
- Self-service merge hardening (when offered): single-use hashed token (30 min) to the
  _old_ account + confirming JWT of the requester, atomic transaction, generic
  anti-enumeration responses, rate limits.
- Cross-tenant: external identity links are tenant-scoped; the same external subject in
  two tenants is two links — never a bridge (matches R88 authz-class lessons).

## 8.3 Bulk import (Part K)

- Pipeline: file → map → validate → stage → commit; **imports are sessions, not
  requests**.
- **`dry_run` defaults to true**; the commit posts the identical payload with
  `dry_run:false`. Strongest parity trick: _dry-run = commit-with-rollback_ — one code
  path, structural parity. Stale previews rejected (`dry_run_stale`) via a data
  fingerprint; Idempotency-Key supported.
- Both atomic and partial modes are legitimate (the issue asks for both): atomic =
  reject-on-any-error; partial = accept valid rows; hybrid for scale = 500-row
  transaction chunks, failed chunk replayed row-by-row so only true failures mark
  failed; lock matched records in id order; retry chunk on deadlock.
- **Collect all errors** (user wants all 200, not the first), 1-indexed + header row
  numbers, downloadable error CSV = original rows + error column, **CSV-injection
  sanitization** on every cell of the report.
- Idempotent re-upload via caller `external_id` in a nullable column with a partial
  unique index: matched-unchanged rows skip, drifted fields update.
- Streaming parse (flat memory), batched lookups (one query per chunk, not per row),
  header-based column mapping (order-agnostic, extra columns ignored, missing required
  column fails the file before any row), BOM/CRLF tolerance.

## 8.4 Governed warehouse export (Part L)

- Reference points: **Stripe Data Pipeline** (choose which reports/metrics to export,
  scheduled refresh ~3h, freshness/last-export timestamps as first-class API surface)
  and Fivetran (incremental/CDC everywhere; **field allowlisting = connector-level
  column blocking/hashing**, since transformation happens downstream).
- Design consequences: exports are **incremental streams or snapshots with explicit
  cursors**; per-destination **field allowlist enforced at serialization time** (same
  `_card_fields`-style total-coverage trap as R82 — every exported field must be
  individually allowlisted, response-model-bound); tenant boundary enforced in the
  query, not the destination; export freshness observable; export definitions
  versioned and audited.

---

# Recommendations for OpenSkill Studio

**R1 — One connection model, Nango-shaped.** `IntegrationProvider` (catalog row ≈
providers.yaml entry: category, auth_mode, declared capabilities, config JSON-Schema) /
`IntegrationConnection` (org-scoped instance, status, connection-id indirection) /
`ConnectionCredential` (encrypted via existing `core/crypto.py`, write-only, refresh
under a per-connection lock) / `SyncProfile` + `MappingProfile` / `SyncRun` (Airbyte-
vocabulary state: per-stream cursor blob, checkpoint timestamps, counts, error class).

**R2 — SSO**: organization-centric connections with per-connection cert pinning, DNS
TXT domain verification (one org per verified domain), metadata-URL polling for cert
rotation with overlap, enforced-SSO policy flag + break-glass account outside the IdP
path, full §1.2 hardening list as test cases. OIDC via authlib; SAML via python3-saml
or pysaml2 behind an internal interface that normalizes both to one verified-identity
struct.

**R3 — SCIM**: scim2-models + own FastAPI router; `active:false` ⇒ same path as
DELETE ⇒ soft-deactivate + immediate session sweep (reuse R88 revocation discipline);
lenient PATCH parsing; delta group membership in transactions; 409/uniqueness; scim2-
tester in CI.

**R4 — Canonical roster objects** (institution, term, class, enrollment, instructor)
shaped so OneRoster 1.2 is a near-identity mapping; SIS connectors pull-only;
per-district (per-connection) failure isolation; conflict report is a first-class
sync artifact.

**R5 — Event mesh**: CloudEvents 1.0 envelope over the existing outbox;
`com.openskill.{entity}.{action}` types, versioned via type suffix; Standard-Webhooks
signing (`webhook-id/timestamp/signature`, HMAC-SHA256 over `id.ts.payload`,
multi-sig rotation, 5-min replay window); Svix retry ladder + auto-disable + DLQ +
replay + attempt log extending the existing `WebhookSubscription`.

**R6 — Sync engine**: at-least-once with destination-confirmed checkpoints; per-field
source-of-truth policy (`ours` / `theirs` / `most_recent` / `prefer_X_unless_blank`),
default one-way, bidirectional opt-in per field; echo suppression via last-outbound-
write comparison; tombstones as soft events, never cascade hard deletes from external
systems (SCIM soft-delete rule generalizes).

**R7 — Mapping**: structured JSONB mapping documents with JMESPath leaf expressions
only, evaluator caps, preview-against-sample endpoint, no tenant code execution.

**R8 — Security backbone**: centralized SSRF-safe egress client used by both webhook
dispatch and connectors (resolve-validate-pin, every dispatch); identity resolution on
stable IdP subject + verified email only + admin confirmation for ambiguity; field
allowlists for exports with total-coverage tests (R82 pattern); audit log on every
admin mapping/connection mutation.

## Anti-patterns (observed across the field)

1. Global SAML certificate trust across tenants (cross-tenant assertion forgery).
2. Hard-deleting on SCIM DELETE / treating PATCH-deactivate differently from DELETE /
   deprovisioning without session revocation.
3. Full-replace group membership sync (timeout ⇒ silent half-written groups).
4. Email-string-based identity linking without verification-assurance checks; re-linking
   on email change.
5. Webhook URL validated only at registration time (DNS rebinding on retry); unsigned
   delivery ids used for dedup; "test webhook" buttons that fetch unvalidated URLs.
6. Blind last-write-wins on semantically directional fields; bidirectional-by-default
   field mappings; missing echo suppression (infinite sync loops).
7. Cursor advanced on send rather than on destination-confirmed commit (data loss on
   crash).
8. Arbitrary tenant code in mapping/transform layers.
9. Common models without raw-data escape hatches (forces connector forks); connector
   auto-upgrades pushed to consumers.
10. Export field filtering as a denylist or applied downstream of serialization
    (new fields leak by default — R82's `_card_fields` lesson at warehouse scale).

## Primary sources

- WorkOS: [SSO](https://workos.com/docs/sso) · [domain verification](https://workos.com/docs/domain-verification/api) · [SAML security best practices](https://workos.com/blog/saml-security-best-practices)
- [Scalekit SAML certificate guide](https://www.scalekit.com/blog/saml-certificates-the-hidden-reason-enterprise-sso-breaks) · [SAML vulnerability handbook](https://www.scalekit.com/blog/a-saml-security-vulnerability-handbook-for-developers) · [SCIM endpoint guide](https://www.scalekit.com/blog/build-scim-endpoint)
- [Atlassian break-glass accounts](https://support.atlassian.com/organization-administration/docs/using-a-break-glass-account-for-emergency-admin-access/)
- [Okta SCIM 2.0](https://developer.okta.com/docs/api/openapi/okta-scim/guides/scim-20) · [Clerk SCIM guide](https://clerk.com/articles/scim-2-0-explained-a-practical-guide-for-saas-auth) · [SCIM deprovisioning pitfalls](https://ssojet.com/blog/scim-deprovisioning-saas-guide) · [soft-delete draft](https://datatracker.ietf.org/doc/html/draft-ansari-scim-soft-delete-00)
- [scim2-models](https://github.com/python-scim/scim2-models) · [scim2-server](https://github.com/python-scim/scim2-server) · [scim2-filter-parser](https://pypi.org/project/scim2-filter-parser/)
- [OneRoster v1.2](https://www.imsglobal.org/spec/oneroster/v1p2) · [LTI Advantage overview](https://www.imsglobal.org/lti-advantage-overview) · [LTI OIDC launch](https://andyfmiller.com/2018/12/28/launching-an-lti-1-3-resource-link-using-openid-connect-third-party-login/) · [Canvas LTI JWT](https://cbennell.com/posts/whats-in-a-canvas-lms-lti-1-3-jwt/)
- [Clever integration types](https://dev.clever.com/docs/integration-types) · [ClassLink explained](https://www.teachfloor.com/blog/what-is-classlink) · [Edlink Clever functionality](https://ed.link/docs/providers/clever/functionality)
- [Merge common models](https://www.merge.dev/features/common-models) · [Merge supplemental data](https://docs.merge.dev/merge-unified/supplemental-data/overview) · [Nango](https://github.com/NangoHQ/nango) · [Nango internals](https://roopeshsn.com/bytes/how-nango-built-an-open-source-unified-api-platform)
- [Prismatic component publishing](https://prismatic.io/docs/custom-connectors/publishing/) · [Prismatic versioning](https://prismatic.io/blog/how-to-use-versioning-in-prismatic/)
- [Svix security](https://docs.svix.com/security) · [Svix retries](https://www.svix.com/resources/webhook-best-practices/retries/) · [Standard Webhooks](https://www.standardwebhooks.com/) · [CloudEvents spec](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md) · [CloudEvents primer](https://github.com/cloudevents/spec/blob/main/cloudevents/primer.md)
- [Airbyte protocol](https://docs.airbyte.com/platform/understanding-airbyte/airbyte-protocol) · [resumability](https://docs.airbyte.com/platform/understanding-airbyte/resumability) · [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes)
- [Stacksync HubSpot↔Salesforce guide](https://www.stacksync.com/blog/hubspot-and-salesforce-sync-the-complete-guide-to-bi-directional-integration) · [hotglue bidirectional sync](https://hotglue.com/blog/bidirectional-integration-sync-guide) · [Truto loop-free HubSpot sync](https://truto.one/blog/how-to-sync-customer-data-bidirectionally-between-your-app-and-hubspot/)
- [Truto JSONata mapping guide](https://truto.one/blog/step-by-step-developer-guide-mapping-custom-objects-with-jsonata/)
- [Stytch SSRF defense](https://stytch.com/blog/securing-identity-apis-against-ssrf/) · [webhook SSRF explained](https://safeguard.sh/resources/blog/ssrf-via-webhooks-explained) · [LoginRadius account linking](https://www.loginradius.com/blog/identity/account-linking-social-login-ux)
- [Idempotent bulk import pipelines](https://dev.to/hammadxcm/designing-idempotent-bulk-import-pipelines-e164-vin-and-the-rest-1man) · [CSV import pipeline guide](https://johal.in/csv-import-pipeline-validation-guide) · [scalable CSV importers](https://mfyz.com/designing-scalable-csv-importers-what-a-good-importer-should-do/)
- [Stripe Data Pipeline](https://stripe.com/data-pipeline)

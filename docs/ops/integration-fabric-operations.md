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
- Failed attempts keep a sanitized 500-char response snippet in the
  attempts view — first stop when a receiver misbehaves.
- Replay: any terminal delivery can be replayed; replays are flagged
  (`replay_of`) and exempt from the one-original-per-(event,subscription)
  uniqueness.

## 4b. Editing and removing resources (R77-R84)

Every admin resource is full CRUD:

- Webhook subscriptions: PATCH edits url/events or re-enables an
  auto-disabled endpoint WITHOUT rotating the secret; DELETE removes.
- Export streams: PATCH edits allowlist/anonymize/schedule or disables;
  DELETE removes the stream + run history (bucket objects stay).
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

## 6. Scheduled jobs (worker crons)

| job                   | schedule        | does                                                             |
| --------------------- | --------------- | ---------------------------------------------------------------- |
| intg_domain_sweep     | :07/:22/:37/:52 | DNS-poll pending domains, expire after 7d                        |
| intg_scheduled_syncs  | :03/:33         | trigger due hourly/daily sync profiles                           |
| intg_stale_run_reaper | :09/:39         | fail runs stuck in running                                       |
| intg_conn_health      | :14/:44         | ping active/degraded connections; alert on unhealthy transition  |
| intg_retention        | 03:52           | age out terminal deliveries (90d), events/runs/row-errors (180d) |
| intg_metadata_refresh | 05:37           | re-poll SAML IdP metadata (cert rotation)                        |
| intg_cert_expiry      | 06:18           | 30-day cert expiry alerts                                        |
| intg_exports          | 02:47           | run due daily export streams                                     |

All registered names are pinned by `test_every_fabric_sweep_has_a_registered_cron`.

## 7. Health and alerting

`GET /orgs/{org}/integrations/health` (the hub strip polls it): connection
status counts, disabled subscriptions, pending/exhausted deliveries,
identity-queue depth, 24h sync failures, active SSO count.

Alertable mesh events to subscribe to:
`integration.delivery.exhausted`, `integration.subscription.auto_disabled`,
`integration.connection.unhealthy`, `integration.sso.cert_expiring`,
`integration.sso.backchannel_logout`.

## 8. Security posture (what to tell the auditor)

Single-egress SSRF discipline (resolve → validate every IP → dial pinned
literal with Host/SNI; mixed public+private resolution refused; enforced by
a lint test), write-only Fernet credential envelopes, uniform-404 IDOR
walls, per-route rate limits on every unauthenticated protocol surface
(guard test), XSW-safe SAML (only the signed subtree is consumed; exclusive
c14n), nonce/state single-use with replay caches, SCIM deprovision sweeps
sessions, export allowlist-built projections with org-salted hashing, and
~200 hand-rolled mutation-probe killers across all nine fabric cores.

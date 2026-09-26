# Ecosystem Intelligence — Operator Handbook

Practical day-to-day guide for platform operators. Design rationale lives in
[ADR-016](../design/016-ecosystem-intelligence.md); Prometheus alerts in
[ecosystem-alerts.md](./ecosystem-alerts.md). Everything below is under
`/dashboard/ecosystem` (platform-admin actions marked ⚙).

## 1. Connect a source ⚙

Sources → Register source. Pick the adapter (HuggingFace, GitHub releases,
JSON catalog, RSS/changelog, manual, …), a trust level, and the base URL —
which is SSRF-validated at registration AND re-validated on every fetch.
Rules of thumb:

- `trust_level` drives auto-resolution: only `official` sources auto-merge
  exact-id alias hits; everything else queues for human review.
- Sync now / Replay: "Sync now" fetches fresh; "Replay" re-runs the CURRENT
  parser over retained raw snapshots (append-only — a parser upgrade creates
  superseding observations, never rewrites).
- A source that keeps failing trips the circuit breaker (status `error`);
  re-activating it resets the failure counter. `eco_sources_stale` alerts
  when an active source is overdue by 3× its interval.

## 2. Work the discovery queue ⚙

Discoveries shows the append-only observation ledger and the entity-
resolution queue.

- **Verify** confirms an observation is real (bulk: "Verify all shown").
- **Resolution candidates**: Confirm merges into the proposed entity
  ("view target" shows exactly what you'd merge into) or registers a NEW
  canonical entity; Reject discards. LLM suggest is a tie-breaker for
  no-match candidates — suggestion only, never auto-merges.
- **LLM-assisted extraction**: paste an announcement/changelog against a
  manual/internal source; extracted observations arrive unverified and
  confidence-capped — the queue above is the gate.

## 3. Govern the catalog ⚙

Catalog → Inspect an entity for its scorecard (independent PASS/WARN/FAIL
checks with evidence), source conflicts (arbitrate a field by choosing the
winning value), price trends, merge (duplicate → survivor), and lifecycle
moves (deprecating requires a reason; retired entities never rank as
replacement candidates). Every irreversible action lands in the commercial
audit trail.

## 4. Subscribe and get notified

Watchlists are the notification primitive:

- Quick-watch any entity from the catalog (👁 Watch).
- Noise controls per list: severity threshold + 7-day mute.
- **Org-attached lists** (create-form selector) additionally fan out over
  the org's webhooks and appear in every org member's change feed; the org's
  owner/admin can manage them.
- Per-entity Atom feed: Inspect → "subscribe (.atom)". Deprecation calendar:
  Watchlists → "subscribe (.ics)".

## 5. Change triage ⚙

Change Feed lists typed change events (severity-filtered, cursor-paginated,
`?entity=` deep-linkable). Acknowledge clears an item from the ops queue
(bulk: "Acknowledge all shown"); `eco_changes_unacknowledged` alerts on
backlog. Acknowledgement is an ops-triage flag, not a per-user read state.

## 6. Security advisories ⚙

Security → register an advisory (ref, severity, affected name + optional
semver range). Matching is exact-name/alias with FAIL-OPEN ranges — an
unparseable range still counts as affected. Watchers of affected entities
are notified through the normal fan-out. Mark mitigated / dismiss when
resolved.

## 7. Replacements & rollouts ⚙

Components → Replacements ranks candidates for a deprecated entity
(hard-incompatible ones are never approvable). Rollouts gate promotion on
guardrails (min samples + per-dimension thresholds vs the baseline);
`evaluate` re-compares, `promote/reject` decides — every decision audited.
Impact analyses show blast radius with SLA deadlines (`eco_impact_open`).

## 8. Exports & integration

- `GET /api/v1/ecosystem/export` — the full catalog document (content-hashed,
  totals + truncation flags; the integration currency). Schema
  `openskill.eco.catalog/v1` evolves ADDITIVELY: new fields (e.g. per-entity
  `metadata.curated`) may appear under the same version; removals or type
  changes bump the version. Parse tolerantly.
- `GET /api/v1/ecosystem/export/changes.atom?entity_id=&token=` — Atom for
  feed readers, which cannot send Bearer headers: mint a narrow-scope token
  via `GET /api/v1/ecosystem/export/feed-token` (365-day expiry, feed-only)
  and append it as `?token=`. The same token opens the read-only export/subscription surfaces: `changes.atom`, `deprecation-calendar.ics`, and `GET /export`. Access tokens are rejected in the query string
  by design — a leaked feed URL only ever exposes the change feed. Rotate by
  minting again; old tokens expire rather than being revoked server-side.
- Both polling surfaces honor conditional GET (R235): send back the
  response `ETag` as `If-None-Match` and a 304 saves the transfer. The
  export ETag equals the body's `content_hash`.
- `GET /api/v1/ecosystem/export/changes?since=&since_id=` — poll this
  instead of re-downloading the world. The cursor is (timestamp, id): always
  pass BOTH `next_since` and `next_since_id` back, or batch-inserted rows
  tied on the boundary timestamp would be skipped.
- Scope note: the delta stream carries EXTERNAL change events. Curation
  edits (capability mappings, alias fixes) surface through the full export's
  `content_hash` changing — re-pull on hash drift.
- `changes.atom` (global, severity- or entity-filtered), `audit.csv`,
  `deprecation-calendar.ics`, benchmark suite export/import (portable JSON).

## 9. Health

`/ecosystem/ops/metrics` is Prometheus-scrapeable (per-metric TYPE lines);
Prometheus scrapes `/api/v1/ecosystem/ops/metrics` with an ADMIN feed
token in the query string (R247) — access tokens expire in minutes:

```yaml
scrape_configs:
  - job_name: openskill-eco
    metrics_path: /api/v1/ecosystem/ops/metrics
    params:
      token: ["<admin feed token from GET /export/feed-token>"]
```

Alert rules and per-alert runbooks live in ecosystem-alerts.md. Crons run
off-peak minutes — source sweep (4/19/34/49), impact SLA (26/56), rollout
eval (11/41), stuck runs (53), telemetry window (58, hourly production
aggregation + divergence comparison), availability probes for watched
entities (14/44), retention (03:41). The outbox dead-letters after max
attempts; dead letters are the `eco_outbox_failed` gauge
(EcoOutboxDeadLetters alert), listed and requeued via
`/api/v1/platform/outbox/failed` and `/api/v1/platform/outbox/{id}/requeue`.

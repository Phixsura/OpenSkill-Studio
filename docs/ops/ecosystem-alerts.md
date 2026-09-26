# Ecosystem Intelligence — Alert Runbook (ADR-016 §41)

Scrape `GET /api/v1/ecosystem/ops/metrics` (platform-admin token) — plaintext
gauges prefixed `eco_`. Below are the recommended Prometheus alert rules and,
for each, what the on-call operator actually does. Every alert maps to an
in-product surface; none require shell access.

## Prometheus rules

```yaml
groups:
  - name: ecosystem-intelligence
    rules:
      - alert: EcoMetricsScrapeDown
        expr: up{job="openskill-eco"} == 0
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "The eco metrics endpoint is not scrapeable"
          runbook: "Every eco alert below goes blind while this fires. Check the API, then the admin feed token in scrape_configs (365-day expiry; a demoted/suspended admin also invalidates it) — mint a fresh one via GET /api/v1/ecosystem/export/feed-token."

      - alert: EcoSourcesStale
        expr: eco_sources_stale > 0
        for: 30m
        labels: { severity: warning }
        annotations:
          summary: "{{ $value }} active sources overdue by 3× their sync interval"
          runbook: "Dashboard → Sources: check last error, adapter_key, vendor status page. A dead vendor is a config change (swap adapter_key), not a code change."

      - alert: EcoEntitiesUnreachable
        expr: eco_availability_unreachable > 0
        for: 30m
        labels: { severity: warning }
        annotations:
          summary: "{{ $value }} watched entities' latest availability probe is unreachable"
          runbook: "Catalog → Inspect the entity; a sustained unreachable status usually precedes a provider incident or a sunset (probes run at :14/:44)."

      - alert: EcoSourcesInError
        expr: eco_sources_error > 0
        for: 15m
        labels: { severity: warning }
        annotations:
          summary: "{{ $value }} sources in error state"
          runbook: "Sources page → error detail. Rate-limit errors self-heal; schema errors need a parser_version bump."

      - alert: EcoOutboxBacklog
        expr: eco_outbox_pending > 100
        for: 10m
        labels: { severity: critical }
        annotations:
          summary: "eco.* outbox backlog {{ $value }} — worker stalled?"
          runbook: "Check the control-plane worker process. Backlog drains automatically once the worker is back; messages are idempotent."

      - alert: EcoSecurityCriticalOpen
        expr: eco_security_critical_open > 0
        for: 0m
        labels: { severity: critical }
        annotations:
          summary: "{{ $value }} unacknowledged security-critical changes"
          runbook: "Change Feed filtered to security_critical; acknowledge after triage. Security page for structured advisories + affected entities."

      - alert: EcoAdvisoriesOpen
        expr: eco_security_advisories_open > 0
        for: 24h
        labels: { severity: warning }
        annotations:
          summary: "{{ $value }} advisories open for >24h"
          runbook: "Security page → affected entities → mitigate (lifecycle transition of hit entities is a separate, human decision) or dismiss with reason."

      - alert: EcoReviewDebtGrowing
        expr: eco_resolution_pending > 50 or eco_pricing_unreviewed > 50
        for: 6h
        labels: { severity: warning }
        annotations:
          summary: 'Curation debt: resolution={{ with query "eco_resolution_pending" }}{{ . | first | value }}{{ end }} pricing={{ with query "eco_pricing_unreviewed" }}{{ . | first | value }}{{ end }}'
          runbook: "Discoveries page bulk-confirm/reject; Pricing page reconcile. Debt hides real changes — keep under 50."

      - alert: EcoBenchmarkQueueStuck
        expr: eco_benchmark_queue > 0
        for: 2h
        labels: { severity: warning }
        annotations:
          summary: "Benchmark runs queued/running for >2h"
          runbook: "Benchmark Lab → runs. Cancel truly stuck queued runs (fence-safe); a 'running' run older than its budget window means the worker died mid-claim — it will NOT double-bill on retry (claim fencing)."

      - alert: EcoImpactSlaBreach
        expr: eco_impact_open > 0
        for: 48h
        labels: { severity: warning }
        annotations:
          summary: "Impact analyses open >48h (SLA escalation should have fired)"
          runbook: "Components → Impact. The eco_impact_sla cron already notified admins at deadline; this alert is the backstop for ignored escalations."

      - alert: EcoInjectionFlagsUnreviewed
        expr: eco_injection_flagged_unverified > 0
        for: 12h
        labels: { severity: warning }
        annotations:
          summary: "{{ $value }} injection-flagged observations awaiting human review"
          runbook: "Discoveries → filter injection-flagged. Flags are advisory (never auto-blocking) but must not rot: verify or reject."
```

## Metric inventory

All from `overview()` flattened as `eco_<key>[_<subkey>]`, plus:

| Metric                                      | Meaning                                    |
| ------------------------------------------- | ------------------------------------------ |
| `eco_sources_active` / `_paused` / `_error` | source states                              |
| `eco_availability_unreachable`              | entities whose latest probe is unreachable |
| `eco_sources_stale`                         | active sources overdue by 3× sync interval |
| `eco_discoveries_7d`                        | observations in the last 7 days            |
| `eco_observations_unverified`               | review debt (observations)                 |
| `eco_injection_flagged_unverified`          | flagged + unverified (advisory heuristics) |
| `eco_changes_unacknowledged`                | change events awaiting ack                 |
| `eco_security_critical_open`                | unacked security-critical changes          |
| `eco_security_advisories_open`              | structured advisories in `open`            |
| `eco_pricing_unreviewed`                    | price observations awaiting reconcile      |
| `eco_resolution_pending`                    | entity-resolution candidates pending       |
| `eco_benchmark_queue`                       | queued+running benchmark runs              |
| `eco_impact_open`                           | open impact analyses                       |
| `eco_replacements_proposed`                 | replacement candidates proposed            |
| `eco_drafts_in_review`                      | component drafts in review                 |
| `eco_rollouts_active`                       | running/evaluating rollout plans           |
| `eco_outbox_pending`                        | pending `eco.*` outbox messages            |

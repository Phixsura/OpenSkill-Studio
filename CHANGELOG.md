# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- Enterprise Integration Fabric (ADR-018, #43) — governed external-system integration:
  - Enterprise SSO: tenant-scoped OIDC (PKCE, back-channel logout) and SAML 2.0
    (signxml XSW-safe SP, metadata auto-refresh, cert-expiry alerts, signed Single
    Logout with replay/freshness guards), domain verification, enforced SSO,
    break-glass admins, deep links and login audit
  - SCIM 2.0 server: Users/Groups incl. /Bulk, /.search, discovery sub-resources,
    attributes projection, Entra/Okta dialects, deactivate≡DELETE with session
    sweep, group→cohort/role maps; scim2-tester conformance 50/0 hard
  - Canonical sync engine: destination-confirmed cursors, idempotent claims,
    tombstones, conflict adjudication, field policies, schedules, inbound
    sync-trigger webhooks (CDC-lite change notification)
  - Connectors: OneRoster SIS, generic REST/ATS/CRM, LTI 1.3 (launch, deep
    linking, AGS grade return, NRPS roster, Dynamic Registration)
  - Event mesh: CloudEvents envelope + per-type payload schemas, Standard-Webhooks
    signing with co-signed rotation, retry ladder, dead-letter, replay, payload
    archive, delivery observability
  - Declarative mapping (JMESPath subset, previews, no user code), canonical model
    JSON-Schema catalog with strict-schema enforcement
  - Bulk CSV/JSON import (streamed 200MB CSV, dry-run with mapped-sample
    confirmation, error reports) and governed warehouse export (NDJSON/Parquet,
    allowlists, org-salted hashing, per-part checksums, incremental cursors)
  - Admin UI: hub, identity, sync, events and data pages with every create form
  - Security: single-egress SSRF discipline, verified-domain gates on
    foreign-account binding, uniform-404 IDOR walls, write-only encrypted
    credentials, protocol rate limits, audit trail
- Verified Talent Graph — capability ontology, scoring engine, evidence tracking
- Skill Passport — privacy-controlled portable credential
- Employment Marketplace — opportunity matching, applications, interviews
- Workforce Intelligence — supply/demand analytics, skill gap predictions
- 100+ API endpoints for talent lifecycle management
- E2E tests covering all talent pages and API mutations
- Security: SSRF protection, rate limiting, CORS, CSP, HSTS

### Fixed

- Passport endpoint graceful degradation for new users
- InterviewScorecard unique constraint
- 5 broken ForeignKey table references
- Input validation on all request schemas

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- **Developer Platform** (Issue #44) — complete third-party extension ecosystem
  - Developer accounts, app model with 7-state lifecycle (draft→published→revoked)
  - 13 database tables, 14 API routers, 60+ endpoints
  - Sandbox runtime: subprocess isolation with CPU/memory/time limits, JSON-RPC
  - OAuth2 authorization code flow with scope validation
  - Event dispatch engine: 35 canonical event types, HMAC-signed webhook delivery
  - Provider Adapter SDK & Ecosystem Source Adapter SDK
  - Manifest validation: 42 permission scopes, SSRF protection, UI surface checks
  - Conformance test suite: 10-check automated compliance validation
  - App marketplace: public browse/search with category filtering
  - TypeScript & Python SDKs with Extension SDK (iframe postMessage)
  - Platform admin dashboard with review queue, stats, kill switch
  - Developer documentation page with quick start, SDK examples
  - 138 integration tests covering full E2E lifecycle
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

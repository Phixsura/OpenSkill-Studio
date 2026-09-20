# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
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

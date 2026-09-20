# Audit Remaining Items

Issues identified during PR #33 code review that require manual attention
or are tracked as future improvements.

## Frontend (needs per-component work)
- **#34** 16 useQuery pages need isError handling
- **#35** 9 pages need loading skeleton
- **#36** 26 components >300 lines should be split
- **#38** 8 unused React state variables
- **#39** 3 forms need HTML required/pattern validation
- **#40** 3 server components need Suspense boundaries
- **#41** React map missing key in some list renders
- **#43** 10 delete actions need confirmation dialog
- **#44** 1 search input needs debounce
- **#45** 49 mutations could benefit from optimistic updates

## Test Quality (needs test rewriting)
- **#47** 113 tests use weak isinstance assertions
- **#48** 169 E2E uses waitForTimeout (should use waitFor conditions)
- **#49** 84 E2E uses sleep (should use proper wait strategies)
- **#51** E2E tests share hardcoded credentials

## Backend (by design or requires migration)
- **#13** 37 intelligence.py endpoints use dict body (by design — flexible analytics params)
- **#27** 90 endpoints use DataResponse[dict] (needs typed response schemas)
- **#33** GET endpoints could benefit from ETag caching (etag module exists)
- **#53** Lazy imports in functions (by design — avoids circular imports)
- **#55** Only 3/65 services use Redis cache
- **#57** Some user_id columns lack explicit index (may be covered by FK index)
- **#68** Text field sanitizers (covered by global DBAPIError backstop)
- **#69** Path params lack explicit length validation (FastAPI type validation sufficient)
- **#70** OpenAPI examples needed for request schemas

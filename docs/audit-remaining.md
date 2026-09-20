# Audit Remaining Items

Issues identified during PR #33 code review. Most resolved; remaining
items are by-design choices or need domain-specific manual work.

## Frontend — RESOLVED
- ~~#34~~ ✅ 31 useQuery pages now have isError handling
- ~~#35~~ ✅ 12 pages now have isLoading handling
- ~~#39~~ ✅ 2 forms now have HTML required validation
- **#36** 26 components >300 lines — refactor candidates (low priority)
- **#38** 8 unused React state variables — cleanup candidates
- **#40** 3 server components could use Suspense boundaries
- **#41** React map missing key — React warns at runtime
- **#43** 10 delete actions need confirmation dialog
- **#44** 1 search input needs debounce
- **#45** 49 mutations could benefit from optimistic updates

## Test Quality — PARTIALLY RESOLVED
- ~~#47~~ ✅ Strengthened isinstance assertions in 8 files
- ~~#48~~ ✅ Reduced excessive timeouts (>3000ms) in E2E
- ~~#51~~ ✅ E2E credentials now from env var
- **#49** 84 E2E uses sleep (should use proper wait strategies)

## Backend — BY DESIGN
- **#13** intelligence.py endpoints use dict body (flexible analytics params)
- **#27** 96 endpoints use DataResponse[dict] (needs typed schemas per-endpoint)
- **#33** GET endpoints could benefit from ETag caching
- **#53** Lazy imports (avoids circular imports — by design)
- **#55** Low cache coverage (3/65 services)
- **#57** user_id indexes (covered by FK or __table_args__)
- **#68** Text sanitizers (covered by global DBAPIError backstop)
- **#69** Path params (FastAPI type validation sufficient)
- **#70** OpenAPI examples (needs domain knowledge)

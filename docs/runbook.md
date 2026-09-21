# Operations Runbook

## Service Health
- API: `GET /api/v1/health`
- Frontend: `GET /` (Next.js)

## Common Issues

### Database Connection Pool Exhaustion
- Symptoms: 500 errors, slow responses
- Fix: `docker restart postgres` or increase `DB_POOL_SIZE`

### Redis Connection Failure
- Symptoms: Rate limiting disabled, cache misses
- Fix: `docker restart redis`
- Note: App degrades gracefully — rate limit falls back to in-memory

### S3/MinIO Unavailable
- Symptoms: File upload failures, 500 on media endpoints
- Fix: `docker restart minio`

### High Memory Usage
- Symptoms: OOM kills on pytest/API
- Fix: Reduce worker count, check for connection leaks

## Deployment
1. `git pull origin main`
2. `make install`
3. `make db-migrate`
4. Restart API: `make dev-api`

## Monitoring
- Structured logs via structlog (JSON format in production)
- Health endpoint includes Redis and S3 status

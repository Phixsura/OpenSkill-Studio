# Load Testing

Use k6 or locust for load testing.

## Quick Start

```bash
k6 run --vus 50 --duration 30s scripts/load-test.js
```

## Endpoints to Test
- POST /api/v1/auth/login
- GET /api/v1/talent/passport
- GET /api/v1/talent/opportunities
- POST /api/v1/talent/applications

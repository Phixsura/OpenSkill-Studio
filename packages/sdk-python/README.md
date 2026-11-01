# openskill-sdk — Python SDK

Official Python SDK for the OpenSkill Developer Platform.

## Installation

```bash
pip install openskill-sdk
# or
uv add openskill-sdk
```

## Quick Start

```python
from openskill_sdk import OpenSkillClient

async with OpenSkillClient(api_key="osk_app_...") as client:
    # Fetch cohorts
    cohorts = await client.get("/cohorts", limit=10)

    # Create a submission
    submission = await client.post("/submissions", {
        "project_id": "proj_...",
        "content": {...},
    })
```

## Adapter SDK

Build provider adapters:

```python
from openskill_sdk.adapter import ProviderAdapter

class MyAdapter(ProviderAdapter):
    name = "my-adapter"
    
    async def execute(self, capability, inputs, config, credentials):
        return {"result": "ok"}
    
    async def health_check(self):
        return {"status": "healthy"}
```

## Error Handling

```python
from openskill_sdk.errors import ApiError, AuthError, RateLimitError

try:
    result = await client.get("/protected")
except AuthError:
    print("Authentication failed")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ApiError as e:
    print(f"API error: {e.code} ({e.status_code})")
```

## Features

- **Async-first** — Built on `httpx` for async HTTP
- **Error hierarchy** — Typed errors matching the API
- **Adapter SDK** — Base classes for provider adapters
- **Context manager** — Proper resource cleanup

## License

MIT

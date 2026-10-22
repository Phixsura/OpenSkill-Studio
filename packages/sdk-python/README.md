# openskill-sdk

Python SDK for the OpenSkill Developer Platform.

## Installation

```bash
pip install openskill-sdk
# or
uv add openskill-sdk
```

## Quick Start

### API Client

```python
from openskill_sdk import OpenSkillClient

async with OpenSkillClient(api_key="osk_app_...") as client:
    # Developer account
    account = await client.developer.get_me()

    # App management
    app = await client.apps.create(
        name="My LMS Connector",
        slug="my-lms",
        category="connector",
    )

    # Create a version
    await client.apps.create_version(
        app["id"],
        version="1.0.0",
        manifest={"schema_version": "1.0", "app": {"name": "My LMS"}, "permissions": ["read:cohorts"]},
        content_hash="sha256...",
    )

    # Browse marketplace
    result = await client.marketplace.browse(category="connector")
```

### Provider Adapter

```python
from openskill_sdk import ProviderAdapter, Capability, HealthCheck

class MyVideoAdapter(ProviderAdapter):
    name = "my-video"
    display_name = "My Video Generator"
    version = "1.0.0"
    capabilities = [
        Capability(
            key="text_to_video",
            input_schema={"prompt": "string", "duration": "integer"},
            output_schema={"video_url": "string"},
            pricing={"unit": "second", "cost_per_unit": 0.05},
        )
    ]

    async def execute(self, capability, inputs, config, credentials, *, idempotency_key=""):
        api_key = credentials["API_KEY"]
        # ... call your provider API ...
        return {
            "video_url": "https://...",
            "__usage__": [{"usage_type": "video_seconds", "quantity": 10}],
        }

    async def health_check(self):
        return HealthCheck(status="healthy", latency_ms=42)
```

### Ecosystem Source Adapter

```python
from openskill_sdk import EcosystemSourceAdapter, SourceRecord

class MyTalentSource(EcosystemSourceAdapter):
    name = "my-talent-db"
    source_type = "talent_directory"

    async def fetch_records(self, config, credentials, *, since=None, limit=100):
        # ... fetch from your data source ...
        return [
            SourceRecord(external_id="t-001", data={"name": "Alice"}, source_type="talent_directory"),
        ]
```

## License

MIT

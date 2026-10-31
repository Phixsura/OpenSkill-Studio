# @openskill/sdk — TypeScript SDK

Official TypeScript SDK for the OpenSkill Developer Platform.

## Installation

```bash
npm install @openskill/sdk
# or
pnpm add @openskill/sdk
```

## Quick Start

```typescript
import { OpenSkillClient } from '@openskill/sdk';

const client = new OpenSkillClient({
  apiKey: 'osk_app_...',
  baseUrl: 'https://api.openskill.studio',
});

// Fetch cohorts
const cohorts = await client.get('/cohorts', { limit: 10 });

// Create a submission
const submission = await client.post('/submissions', {
  project_id: 'proj_...',
  content: { ... },
});

await client.close();
```

## Extension SDK (UI Extensions)

For sandboxed iframe UI extensions:

```typescript
import { OpenSkillExtension } from '@openskill/sdk/extension';

const ext = new OpenSkillExtension({
  origin: 'https://app.openskill.studio',
});

ext.on('context_changed', (ctx) => {
  console.log('Org:', ctx.orgId, 'Surface:', ctx.surface);
});

const data = await ext.api.get('/cohorts');
ext.ui.toast({ message: 'Loaded!', type: 'success' });
```

## Error Handling

```typescript
import { ApiError, AuthError, RateLimitError } from '@openskill/sdk';

try {
  await client.get('/protected');
} catch (err) {
  if (err instanceof AuthError) {
    console.log('Auth failed:', err.message);
  } else if (err instanceof RateLimitError) {
    console.log('Rate limited, retry after:', err.retryAfter);
  } else if (err instanceof ApiError) {
    console.log('API error:', err.code, err.statusCode);
  }
}
```

## Features

- **Type-safe** — Full TypeScript types for all API endpoints
- **Error hierarchy** — Typed errors: `ApiError`, `AuthError`, `NotFoundError`, `RateLimitError`, `ValidationError`
- **Extension SDK** — Secure postMessage-based communication for iframe UI extensions
- **Async/await** — Modern async API with proper cleanup
- **Context manager** — Use with `using` or manual `close()`

## License

MIT

# @openskill/sdk

TypeScript SDK for the OpenSkill Developer Platform.

## Installation

```bash
npm install @openskill/sdk
# or
pnpm add @openskill/sdk
```

## Quick Start

### API Client

```typescript
import { OpenSkillClient } from "@openskill/sdk";

const client = new OpenSkillClient({
  apiKey: "osk_app_...",
  baseUrl: "https://api.openskill.dev",
});

// Developer account
const account = await client.developer.getMe();

// App management
const app = await client.apps.create({
  name: "My LMS Connector",
  slug: "my-lms",
  category: "connector",
});

// Create a version
await client.apps.createVersion(app.id, {
  version: "1.0.0",
  manifest: { schema_version: "1.0", app: { name: "My LMS" }, permissions: ["read:cohorts"] },
  content_hash: "sha256...",
});

// Browse marketplace
const { data: apps } = await client.marketplace.browse({ category: "connector" });
```

### UI Extension SDK

For building sandboxed UI extensions (iframe-based):

```typescript
import { OpenSkillExtension } from "@openskill/sdk/extension";

const ext = new OpenSkillExtension();

// Listen for context
ext.on("context_changed", (ctx) => {
  console.log("Org:", ctx.orgId, "Surface:", ctx.surface);
});

// Make API calls (scoped to granted permissions)
const cohorts = await ext.api.get("/cohorts", { limit: 10 });

// UI controls
ext.ui.resize({ height: 500 });
ext.ui.toast({ message: "Sync complete!", type: "success" });
ext.ui.navigate("/dashboard/orgs/{orgId}/cohorts");
```

## API Reference

### `OpenSkillClient`

| Method                           | Description                    |
| -------------------------------- | ------------------------------ |
| `developer.getMe()`             | Get current developer account  |
| `developer.create(data)`        | Create developer account       |
| `apps.list(query?)`             | List your apps                 |
| `apps.get(appId)`               | Get app details                |
| `apps.create(data)`             | Create an app                  |
| `apps.update(appId, data)`      | Update an app                  |
| `apps.createVersion(appId, d)`  | Create a version               |
| `apps.listVersions(appId)`      | List versions                  |
| `apps.submitForReview(appId)`   | Submit for platform review     |
| `apps.publish(appId)`           | Publish an approved app        |
| `apps.createApiKey(appId, d)`   | Generate an API key            |
| `apps.listApiKeys(appId)`       | List API keys                  |
| `apps.getStats(appId)`          | Get observability stats        |
| `apps.runConformance(appId)`    | Run conformance checks         |
| `marketplace.browse(query?)`    | Browse published apps          |
| `marketplace.get(appId)`        | Get marketplace app detail     |
| `cohorts.list(orgId, query?)`   | List cohorts                   |
| `projects.list(orgId, query?)`  | List projects                  |

### `OpenSkillExtension`

| Method / Property    | Description                           |
| -------------------- | ------------------------------------- |
| `context`            | Current extension context             |
| `isReady`            | Whether initial context received      |
| `on(event, handler)` | Listen for events (returns unsub fn)  |
| `api.get(path, q?)`  | GET via host API proxy                |
| `api.post(path, b?)` | POST via host API proxy               |
| `api.patch(path, b?)`| PATCH via host API proxy              |
| `api.delete(path)`   | DELETE via host API proxy             |
| `ui.resize(dims)`    | Resize the iframe                     |
| `ui.navigate(path)`  | Navigate host to a page               |
| `ui.toast(opts)`     | Show toast notification               |
| `ui.openModal(opts)` | Open a modal                          |
| `ui.close()`         | Close the extension panel             |
| `destroy()`          | Clean up all listeners                |

## License

MIT

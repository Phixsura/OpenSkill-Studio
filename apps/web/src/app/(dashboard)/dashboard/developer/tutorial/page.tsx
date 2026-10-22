"use client";

import Link from "next/link";

export default function DeveloperTutorialPage() {
  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="mb-2 text-3xl font-bold">Build Your First App</h1>
      <p className="mb-8 text-gray-600 dark:text-gray-400">
        Step-by-step tutorial to build, test, and publish a connector app
      </p>

      {/* Step 1 */}
      <section className="mb-10">
        <h2 className="mb-3 flex items-center gap-3 text-xl font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
            1
          </span>
          Set Up Your Developer Account
        </h2>
        <div className="ml-11">
          <p className="mb-3 text-gray-600 dark:text-gray-400">
            Install the SDK and create your developer identity:
          </p>
          <pre className="mb-3 rounded-lg bg-gray-900 p-4 text-sm text-gray-300">
            {`# Install the SDK
npm install @openskill/sdk

# Or for Python
pip install openskill-sdk`}
          </pre>
          <pre className="rounded-lg bg-gray-900 p-4 text-sm text-gray-300">
            {`import { OpenSkillClient } from '@openskill/sdk';

const client = new OpenSkillClient({
  apiKey: 'YOUR_API_KEY',  // Get this after creating your account
  baseUrl: 'http://localhost:8000',
});

// Create developer account
const account = await client.developer.create({
  display_name: 'My Company',
  slug: 'my-company',
  support_email: 'dev@mycompany.com',
});
console.log('Developer account:', account.id);`}
          </pre>
        </div>
      </section>

      {/* Step 2 */}
      <section className="mb-10">
        <h2 className="mb-3 flex items-center gap-3 text-xl font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
            2
          </span>
          Create Your App
        </h2>
        <div className="ml-11">
          <p className="mb-3 text-gray-600 dark:text-gray-400">
            Define your app with a manifest specifying permissions and capabilities:
          </p>
          <pre className="rounded-lg bg-gray-900 p-4 text-sm text-gray-300">
            {`// Create a connector app
const app = await client.apps.create({
  name: 'My LMS Connector',
  slug: 'my-lms-connector',
  category: 'connector',
  description: 'Sync grades and enrollments with My LMS',
  manifest: {
    schema_version: '1.0',
    app: {
      name: 'My LMS Connector',
      slug: 'my-lms-connector',
      version: '1.0.0',
      category: 'connector',
    },
    permissions: [
      'read:cohorts',
      'read:submissions',
      'write:project_results',
      'subscribe:events',
    ],
    event_subscriptions: [
      'submission.completed',
      'submission.graded',
    ],
    secrets: [
      { key: 'LMS_API_KEY', description: 'Your LMS API key', required: true },
    ],
  },
});
console.log('App created:', app.id);
console.log('OAuth Client ID:', app.oauth_client_id);`}
          </pre>
        </div>
      </section>

      {/* Step 3 */}
      <section className="mb-10">
        <h2 className="mb-3 flex items-center gap-3 text-xl font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
            3
          </span>
          Handle Events
        </h2>
        <div className="ml-11">
          <p className="mb-3 text-gray-600 dark:text-gray-400">
            Set up a webhook endpoint to receive platform events:
          </p>
          <pre className="rounded-lg bg-gray-900 p-4 text-sm text-gray-300">
            {`// Express webhook handler
import { verify_signature } from '@openskill/sdk';

app.post('/webhooks/openskill', (req, res) => {
  // Verify HMAC signature
  const signature = req.headers['x-openskill-signature'];
  const isValid = verify_signature(req.rawBody, signature, WEBHOOK_SECRET);
  if (!isValid) return res.status(401).send('Invalid signature');

  const event = req.body.event;
  console.log('Event:', event.event_type, event.data);

  switch (event.event_type) {
    case 'submission.graded':
      // Sync grade to your LMS
      await syncGrade(event.data.user_id, event.data.grade);
      break;
    case 'submission.completed':
      // Notify your system
      await notifySubmission(event.data.submission_id);
      break;
  }

  res.status(200).send('OK');
});`}
          </pre>
        </div>
      </section>

      {/* Step 4 */}
      <section className="mb-10">
        <h2 className="mb-3 flex items-center gap-3 text-xl font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
            4
          </span>
          Test with Developer Tools
        </h2>
        <div className="ml-11">
          <p className="mb-3 text-gray-600 dark:text-gray-400">
            Use the developer tools to validate and test your app:
          </p>
          <pre className="rounded-lg bg-gray-900 p-4 text-sm text-gray-300">
            {`// Validate your manifest
const validation = await fetch('/api/v1/developer/validate-manifest', {
  method: 'POST',
  body: JSON.stringify({ manifest: myManifest }),
});
// { valid: true, errors: [], warnings: [] }

// Send a test event
await fetch('/api/v1/developer/tools/send-test-event', {
  method: 'POST',
  body: JSON.stringify({
    event_type: 'submission.graded',
    data: { user_id: 'test-user', grade: 85 },
    org_id: 'your-org-id',
  }),
});`}
          </pre>
        </div>
      </section>

      {/* Step 5 */}
      <section className="mb-10">
        <h2 className="mb-3 flex items-center gap-3 text-xl font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
            5
          </span>
          Publish to the Marketplace
        </h2>
        <div className="ml-11">
          <p className="mb-3 text-gray-600 dark:text-gray-400">
            Create a version, submit for review, and publish:
          </p>
          <pre className="rounded-lg bg-gray-900 p-4 text-sm text-gray-300">
            {`// Create a version
await client.apps.createVersion(app.id, {
  version: '1.0.0',
  manifest: myManifest,
  content_hash: sha256OfPackage,
  changelog: 'Initial release',
  signature: ed25519Signature,  // optional
});

// Submit for review (after testing)
await client.apps.submitForReview(app.id);

// Once approved, publish!
await client.apps.publish(app.id);

// Check your app's health
const health = await client.apps.runConformance(app.id);
console.log('Conformance:', health.summary);`}
          </pre>
        </div>
      </section>

      {/* Next Steps */}
      <div className="rounded-xl bg-gray-50 p-8 dark:bg-gray-800">
        <h2 className="mb-4 text-xl font-semibold">Next Steps</h2>
        <div className="grid gap-3 md:grid-cols-3">
          <Link
            href="/dashboard/developer/api-reference"
            className="rounded-lg border bg-white p-4 text-center transition-colors hover:border-blue-500 dark:border-gray-600 dark:bg-gray-700"
          >
            <p className="font-medium">📚 API Reference</p>
            <p className="mt-1 text-xs text-gray-500">60+ endpoints</p>
          </Link>
          <Link
            href="/dashboard/developer/docs"
            className="rounded-lg border bg-white p-4 text-center transition-colors hover:border-blue-500 dark:border-gray-600 dark:bg-gray-700"
          >
            <p className="font-medium">📖 Documentation</p>
            <p className="mt-1 text-xs text-gray-500">Concepts & guides</p>
          </Link>
          <Link
            href="/dashboard/developer/apps"
            className="rounded-lg border bg-white p-4 text-center transition-colors hover:border-blue-500 dark:border-gray-600 dark:bg-gray-700"
          >
            <p className="font-medium">🧩 My Apps</p>
            <p className="mt-1 text-xs text-gray-500">Start building</p>
          </Link>
        </div>
      </div>
    </div>
  );
}

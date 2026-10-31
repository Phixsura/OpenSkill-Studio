"use client";

import { useParams } from "next/navigation";

export default function AppSecretsReferencePage() {
  const { appId } = useParams<{ appId: string }>();

  return (
    <div className="max-w-3xl p-8">
      <h1 className="mb-2 text-2xl font-bold">Secrets Reference</h1>
      <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
        Secrets are configured per-installation by the org admin, not by the developer.
        Define required secrets in your manifest.
      </p>

      <div className="mb-6 rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-3 text-lg font-semibold">How Secrets Work</h2>
        <ul className="list-inside list-disc space-y-2 text-sm text-gray-600 dark:text-gray-400">
          <li>Declare required secrets in your app&apos;s manifest under <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">secrets</code></li>
          <li>Org admins set secret values when installing your app</li>
          <li>Secrets are Fernet-encrypted at rest — never stored in plaintext</li>
          <li>Your sandbox code receives secrets as <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">OPENSKILL_SECRET_&lt;KEY&gt;</code> environment variables</li>
          <li>The API never returns secret values — only metadata (key name, description)</li>
        </ul>
      </div>

      <div className="rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-3 text-lg font-semibold">Manifest Example</h2>
        <pre className="rounded bg-gray-900 p-4 text-xs text-gray-100">
{`{
  "secrets": [
    {
      "key": "LMS_API_KEY",
      "description": "API key for your LMS integration",
      "required": true
    },
    {
      "key": "WEBHOOK_SECRET",
      "description": "Signing key for outbound webhooks"
    }
  ]
}`}
        </pre>
      </div>
    </div>
  );
}

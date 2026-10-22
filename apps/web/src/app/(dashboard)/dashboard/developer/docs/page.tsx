"use client";

import Link from "next/link";

export default function DeveloperDocsPage() {
  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="mb-2 text-3xl font-bold">Developer Documentation</h1>
      <p className="mb-8 text-gray-600 dark:text-gray-400">
        Everything you need to build apps, connectors, and extensions for OpenSkill Studio
      </p>

      {/* Quick Start */}
      <section className="mb-10">
        <h2 className="mb-4 text-xl font-semibold">🚀 Quick Start</h2>
        <div className="space-y-4 rounded-lg border p-6 dark:border-gray-700">
          <div className="flex gap-4">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              1
            </div>
            <div>
              <h3 className="font-medium">Create a Developer Account</h3>
              <p className="mt-1 text-sm text-gray-500">
                Go to{" "}
                <Link href="/dashboard/developer" className="text-blue-600 hover:underline">
                  Developer Portal
                </Link>{" "}
                and register your developer identity.
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              2
            </div>
            <div>
              <h3 className="font-medium">Create an App</h3>
              <p className="mt-1 text-sm text-gray-500">
                Choose a category (connector, workflow adapter, UI extension, etc.) and define your
                app&apos;s manifest with the permissions it needs.
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              3
            </div>
            <div>
              <h3 className="font-medium">Build & Test</h3>
              <p className="mt-1 text-sm text-gray-500">
                Use the TypeScript or Python SDK to build your app. Use the developer tools to send
                test events and validate your manifest.
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              4
            </div>
            <div>
              <h3 className="font-medium">Submit for Review & Publish</h3>
              <p className="mt-1 text-sm text-gray-500">
                Create a version, submit for platform review, and publish to the marketplace.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SDK Installation */}
      <section className="mb-10">
        <h2 className="mb-4 text-xl font-semibold">📦 SDK Installation</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border p-5 dark:border-gray-700">
            <h3 className="mb-3 font-semibold">TypeScript</h3>
            <pre className="rounded bg-gray-900 p-3 text-sm text-green-400">
              npm install @openskill/sdk
            </pre>
            <pre className="mt-3 rounded bg-gray-900 p-3 text-xs text-gray-300">
              {`import { OpenSkillClient } from '@openskill/sdk';

const client = new OpenSkillClient({
  apiKey: 'osk_app_...',
});

const cohorts = await client.cohorts.list(orgId);`}
            </pre>
          </div>
          <div className="rounded-lg border p-5 dark:border-gray-700">
            <h3 className="mb-3 font-semibold">Python</h3>
            <pre className="rounded bg-gray-900 p-3 text-sm text-green-400">
              pip install openskill-sdk
            </pre>
            <pre className="mt-3 rounded bg-gray-900 p-3 text-xs text-gray-300">
              {`from openskill_sdk import OpenSkillClient

async with OpenSkillClient(
    api_key="osk_app_..."
) as client:
    account = await client.developer.get_me()`}
            </pre>
          </div>
        </div>
      </section>

      {/* API Reference */}
      <section className="mb-10">
        <h2 className="mb-4 text-xl font-semibold">📚 API Reference</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {[
            { title: "Developer Accounts", desc: "Register and manage developer identity", endpoints: 5 },
            { title: "Apps", desc: "Create, update, and manage app lifecycle", endpoints: 10 },
            { title: "Versions", desc: "Version management with semver", endpoints: 3 },
            { title: "Installations", desc: "Install/uninstall apps in orgs", endpoints: 6 },
            { title: "API Keys", desc: "Create and manage API keys", endpoints: 3 },
            { title: "Event Subscriptions", desc: "Subscribe to platform events", endpoints: 3 },
            { title: "Automation Rules", desc: "Event-driven automation", endpoints: 3 },
            { title: "Secrets", desc: "Encrypted secret management", endpoints: 3 },
            { title: "Marketplace", desc: "Browse and discover apps", endpoints: 2 },
            { title: "OAuth 2.0", desc: "Authorization code flow", endpoints: 2 },
            { title: "Webhooks", desc: "HMAC-signed event delivery", endpoints: 2 },
            { title: "Observability", desc: "Stats, metrics, conformance", endpoints: 4 },
          ].map((section) => (
            <div key={section.title} className="rounded border p-3 dark:border-gray-700">
              <h3 className="font-medium">{section.title}</h3>
              <p className="text-sm text-gray-500">{section.desc}</p>
              <p className="mt-1 text-xs text-gray-400">{section.endpoints} endpoints</p>
            </div>
          ))}
        </div>
      </section>

      {/* Concepts */}
      <section className="mb-10">
        <h2 className="mb-4 text-xl font-semibold">💡 Key Concepts</h2>
        <div className="space-y-4">
          {[
            {
              title: "Manifest",
              desc: "Every app declares its capabilities, permissions, and configuration in a manifest.json. The platform validates this at submission time.",
            },
            {
              title: "Sandbox Runtime",
              desc: "Third-party code runs in an isolated subprocess with CPU, memory, and time limits. No direct database access — all data flows through scoped API calls.",
            },
            {
              title: "Permission Scopes",
              desc: "42 granular scopes control what an app can access. Tenants approve specific scopes at installation time.",
            },
            {
              title: "Event System",
              desc: "35 canonical event types across all platform domains. Apps subscribe to events and receive HMAC-signed webhook deliveries.",
            },
            {
              title: "UI Extensions",
              desc: "8 extension surfaces (dashboard cards, sidebars, tools) rendered in sandboxed iframes. The Extension SDK handles host communication via postMessage.",
            },
            {
              title: "Conformance Suite",
              desc: "Automated checks validate manifest compliance, version health, security posture, and runtime behavior.",
            },
          ].map((concept) => (
            <div key={concept.title} className="rounded-lg border p-4 dark:border-gray-700">
              <h3 className="font-semibold">{concept.title}</h3>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{concept.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Links */}
      <section>
        <h2 className="mb-4 text-xl font-semibold">🔗 Resources</h2>
        <div className="grid gap-3 md:grid-cols-3">
          <Link
            href="/dashboard/developer"
            className="rounded-lg border p-4 text-center transition-colors hover:border-blue-500 dark:border-gray-700"
          >
            <p className="font-medium">Developer Portal</p>
            <p className="text-sm text-gray-500">Manage your apps</p>
          </Link>
          <Link
            href="/dashboard/developer/apps"
            className="rounded-lg border p-4 text-center transition-colors hover:border-blue-500 dark:border-gray-700"
          >
            <p className="font-medium">My Apps</p>
            <p className="text-sm text-gray-500">Build and publish</p>
          </Link>
          <Link
            href="/marketplace/apps"
            className="rounded-lg border p-4 text-center transition-colors hover:border-blue-500 dark:border-gray-700"
          >
            <p className="font-medium">Marketplace</p>
            <p className="text-sm text-gray-500">Browse all apps</p>
          </Link>
        </div>
      </section>
    </div>
  );
}

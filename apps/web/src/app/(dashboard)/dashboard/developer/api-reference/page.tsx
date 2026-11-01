"use client";

import { useState } from "react";

const API_SECTIONS = [
  {
    title: "Developer Accounts",
    endpoints: [
      { method: "POST", path: "/developer/accounts", desc: "Create developer account" },
      { method: "GET", path: "/developer/accounts/me", desc: "Get your developer account" },
      { method: "PATCH", path: "/developer/accounts/{id}", desc: "Update developer account" },
      { method: "GET", path: "/developer/accounts", desc: "List all developer accounts" },
    ],
  },
  {
    title: "Apps",
    endpoints: [
      { method: "POST", path: "/developer/apps", desc: "Create app" },
      { method: "GET", path: "/developer/apps", desc: "List your apps" },
      { method: "GET", path: "/developer/apps/{id}", desc: "Get app details" },
      { method: "PATCH", path: "/developer/apps/{id}", desc: "Update app" },
      { method: "POST", path: "/developer/apps/{id}/submit", desc: "Submit for review" },
      { method: "POST", path: "/developer/apps/{id}/publish", desc: "Publish app" },
      { method: "POST", path: "/developer/apps/{id}/deprecate", desc: "Deprecate app" },
      { method: "POST", path: "/developer/apps/{id}/revoke", desc: "Revoke (kill switch)" },
    ],
  },
  {
    title: "Versions",
    endpoints: [
      { method: "POST", path: "/developer/apps/{id}/versions", desc: "Create version" },
      { method: "GET", path: "/developer/apps/{id}/versions", desc: "List versions" },
      { method: "GET", path: "/developer/apps/{id}/versions/{vid}", desc: "Get version" },
    ],
  },
  {
    title: "API Keys",
    endpoints: [
      { method: "POST", path: "/developer/apps/{id}/api-keys", desc: "Create API key" },
      { method: "GET", path: "/developer/apps/{id}/api-keys", desc: "List API keys" },
      { method: "DELETE", path: "/developer/apps/{id}/api-keys/{kid}", desc: "Revoke key" },
    ],
  },
  {
    title: "Installations",
    endpoints: [
      { method: "POST", path: "/orgs/{orgId}/apps/install", desc: "Install app" },
      { method: "GET", path: "/orgs/{orgId}/apps/installations", desc: "List installations" },
      { method: "PATCH", path: "/orgs/{orgId}/apps/installations/{id}", desc: "Update config" },
      { method: "POST", path: "/orgs/{orgId}/apps/installations/{id}/upgrade", desc: "Upgrade version" },
      { method: "DELETE", path: "/orgs/{orgId}/apps/installations/{id}", desc: "Uninstall" },
    ],
  },
  {
    title: "Secrets",
    endpoints: [
      { method: "PUT", path: "/orgs/{orgId}/apps/installations/{id}/secrets", desc: "Set secret" },
      { method: "GET", path: "/orgs/{orgId}/apps/installations/{id}/secrets", desc: "List secrets" },
      { method: "DELETE", path: "/orgs/{orgId}/apps/installations/{id}/secrets/{key}", desc: "Delete secret" },
    ],
  },
  {
    title: "Event Subscriptions",
    endpoints: [
      { method: "POST", path: "/orgs/{orgId}/apps/installations/{id}/events", desc: "Subscribe" },
      { method: "GET", path: "/orgs/{orgId}/apps/installations/{id}/events", desc: "List" },
      { method: "DELETE", path: "/orgs/{orgId}/apps/installations/{id}/events/{sid}", desc: "Unsubscribe" },
    ],
  },
  {
    title: "Automation Rules",
    endpoints: [
      { method: "POST", path: "/orgs/{orgId}/apps/installations/{id}/rules", desc: "Create rule" },
      { method: "GET", path: "/orgs/{orgId}/apps/installations/{id}/rules", desc: "List rules" },
      { method: "DELETE", path: "/orgs/{orgId}/apps/installations/{id}/rules/{rid}", desc: "Delete rule" },
    ],
  },
  {
    title: "Observability",
    endpoints: [
      { method: "GET", path: "/developer/apps/{id}/stats", desc: "App stats" },
      { method: "GET", path: "/developer/apps/{id}/health", desc: "Health check" },
      { method: "GET", path: "/developer/apps/{id}/version-adoption", desc: "Version adoption" },
      { method: "GET", path: "/developer/apps/{id}/conformance", desc: "Conformance report" },
      { method: "GET", path: "/developer/apps/{id}/webhook-deliveries", desc: "Delivery log" },
    ],
  },
  {
    title: "Marketplace",
    endpoints: [
      { method: "GET", path: "/marketplace/apps", desc: "Browse apps (public)" },
      { method: "GET", path: "/marketplace/apps/{id}", desc: "App detail (public)" },
    ],
  },
  {
    title: "OAuth 2.0",
    endpoints: [
      { method: "GET", path: "/oauth/authorize", desc: "Authorization code" },
      { method: "POST", path: "/oauth/token", desc: "Token exchange" },
    ],
  },
  {
    title: "Developer Tools",
    endpoints: [
      { method: "POST", path: "/developer/tools/send-test-event", desc: "Send test event" },
      { method: "GET", path: "/developer/tools/event-types", desc: "List event types" },
      { method: "GET", path: "/developer/tools/permissions", desc: "List permissions" },
      { method: "GET", path: "/developer/tools/ui-surfaces", desc: "List UI surfaces" },
      { method: "POST", path: "/developer/tools/generate-fixtures", desc: "Generate fixtures" },
      { method: "POST", path: "/developer/validate-manifest", desc: "Validate manifest" },
      { method: "GET", path: "/developer/openapi.json", desc: "OpenAPI spec" },
    ],
  },
];

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  POST: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  PATCH: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  PUT: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  DELETE: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function ApiReferencePage() {
  const [expanded, setExpanded] = useState<string | null>(null);
  const totalEndpoints = API_SECTIONS.reduce((sum, s) => sum + s.endpoints.length, 0);

  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="mb-2 text-2xl font-bold">API Reference</h1>
      <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
        {API_SECTIONS.length} sections · {totalEndpoints} endpoints · All under{" "}
        <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">/api/v1/</code>
      </p>

      <div className="space-y-4">
        {API_SECTIONS.map((section) => (
          <div key={section.title} className="rounded-lg border dark:border-gray-700">
            <button
              className="flex w-full items-center justify-between px-5 py-4 text-left"
              onClick={() => setExpanded(expanded === section.title ? null : section.title)}
            >
              <div>
                <h2 className="font-semibold">{section.title}</h2>
                <p className="text-xs text-gray-400">{section.endpoints.length} endpoints</p>
              </div>
              <span className="text-gray-400">{expanded === section.title ? "▼" : "▶"}</span>
            </button>
            {expanded === section.title && (
              <div className="border-t px-5 pb-4 pt-2 dark:border-gray-700">
                <div className="space-y-2">
                  {section.endpoints.map((ep) => (
                    <div key={ep.path + ep.method} className="flex items-center gap-3 text-sm">
                      <span
                        className={`w-16 rounded px-2 py-0.5 text-center text-xs font-bold ${METHOD_COLORS[ep.method] ?? ""}`}
                      >
                        {ep.method}
                      </span>
                      <code className="flex-1 font-mono text-xs text-gray-600 dark:text-gray-300">
                        {ep.path}
                      </code>
                      <span className="text-xs text-gray-400">{ep.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

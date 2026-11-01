"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface AppDetail {
  id: string;
  developer_id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  homepage_url: string | null;
  privacy_policy_url: string | null;
  category: string;
  visibility: string;
  status: string;
  manifest: Record<string, unknown> | null;
  oauth_client_id: string | null;
  redirect_uris: string[] | null;
  webhook_url: string | null;
  created_at: string;
  updated_at: string;
}

interface AppVersion {
  id: string;
  app_id: string;
  version: string;
  changelog: string | null;
  content_hash: string;
  review_status: string;
  created_at: string;
}

interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  rate_limit_tier: string;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

const STATUS_ACTIONS: Record<
  string,
  { label: string; endpoint: string; variant: "primary" | "outline" | "destructive" }[]
> = {
  draft: [{ label: "Start Testing", endpoint: "submit", variant: "primary" }],
  testing: [{ label: "Submit for Review", endpoint: "submit", variant: "primary" }],
  approved: [{ label: "Publish", endpoint: "publish", variant: "primary" }],
  published: [
    { label: "Deprecate", endpoint: "deprecate", variant: "outline" },
    { label: "Revoke", endpoint: "revoke", variant: "destructive" },
  ],
};

export default function AppDetailPage() {
  const { appId } = useParams<{ appId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"overview" | "versions" | "keys">("overview");

  const { data: app, isLoading } = useQuery({
    queryKey: ["developer-app", appId],
    queryFn: () => apiWithAuth<{ data: AppDetail }>(`/developer/apps/${appId}`).then((r) => r.data),
  });

  const { data: versionsData } = useQuery({
    queryKey: ["app-versions", appId],
    queryFn: () => apiWithAuth<{ data: AppVersion[] }>(`/developer/apps/${appId}/versions`),
    enabled: activeTab === "versions",
  });

  const { data: keysData } = useQuery({
    queryKey: ["app-api-keys", appId],
    queryFn: () => apiWithAuth<{ data: ApiKey[] }>(`/developer/apps/${appId}/api-keys`),
    enabled: activeTab === "keys",
  });

  const lifecycleMutation = useMutation({
    mutationFn: (endpoint: string) =>
      apiWithAuth(`/developer/apps/${appId}/${endpoint}`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["developer-app", appId] });
    },
  });

  const createKeyMutation = useMutation({
    mutationFn: (data: { name: string; scopes: string[] }) =>
      apiWithAuth<{ data: { key: string; id: string } }>(`/developer/apps/${appId}/api-keys`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["app-api-keys", appId] });
      alert(`API Key created!\n\nKey: ${data.data.key}\n\nSave this — it won't be shown again.`);
    },
  });

  if (isLoading || !app) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-96 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    );
  }

  const actions = STATUS_ACTIONS[app.status] ?? [];
  const versions = versionsData?.data ?? [];
  const keys = keysData?.data ?? [];

  return (
    <div className="max-w-4xl p-8">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{app.name}</h1>
          <p className="mt-1 text-gray-500 dark:text-gray-400">
            {app.slug} · {app.category.replace("_", " ")}
          </p>
          {app.description && (
            <p className="mt-2 text-gray-700 dark:text-gray-300">{app.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-3 py-1 text-sm font-medium ${
              app.status === "published"
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : app.status === "draft"
                  ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                  : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
            }`}
          >
            {app.status}
          </span>
          <span className="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">
            {app.visibility}
          </span>
        </div>
      </div>

      {/* Lifecycle Actions */}
      {actions.length > 0 && (
        <div className="mb-6 flex gap-2">
          {actions.map((action) => (
            <Button
              key={action.endpoint}
              variant={action.variant}
              onClick={() => lifecycleMutation.mutate(action.endpoint)}
              disabled={lifecycleMutation.isPending}
            >
              {action.label}
            </Button>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b dark:border-gray-700">
        <div className="flex gap-4">
          {(["overview", "versions", "keys"] as const).map((tab) => (
            <button
              key={tab}
              className={`border-b-2 px-1 pb-2 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? "border-blue-500 text-blue-600 dark:text-blue-400"
                  : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400"
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                OAuth Client ID
              </h3>
              <p className="mt-1 break-all font-mono text-sm">{app.oauth_client_id ?? "—"}</p>
            </div>
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Webhook URL</h3>
              <p className="mt-1 break-all text-sm">{app.webhook_url ?? "Not configured"}</p>
            </div>
          </div>

          {app.redirect_uris && app.redirect_uris.length > 0 && (
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <h3 className="mb-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                Redirect URIs
              </h3>
              <ul className="space-y-1">
                {app.redirect_uris.map((uri, i) => (
                  <li key={i} className="font-mono text-sm">
                    {uri}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {app.manifest && (
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <h3 className="mb-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                Manifest
              </h3>
              <pre className="max-h-64 overflow-auto rounded bg-gray-50 p-3 text-xs dark:bg-gray-800">
                {JSON.stringify(app.manifest, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Versions Tab */}
      {activeTab === "versions" && (
        <div className="space-y-3">
          {versions.length === 0 ? (
            <p className="py-8 text-center text-gray-500 dark:text-gray-400">
              No versions yet. Create your first version to start testing.
            </p>
          ) : (
            versions.map((v) => (
              <div key={v.id} className="rounded-lg border p-4 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-mono font-semibold">v{v.version}</span>
                    <span
                      className={`ml-2 rounded px-2 py-0.5 text-xs ${
                        v.review_status === "approved"
                          ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                          : v.review_status === "rejected"
                            ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                            : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                      }`}
                    >
                      {v.review_status}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(v.created_at).toLocaleDateString()}
                  </span>
                </div>
                {v.changelog && (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{v.changelog}</p>
                )}
                <p className="mt-1 font-mono text-xs text-gray-400">
                  SHA-256: {v.content_hash.slice(0, 16)}…
                </p>
              </div>
            ))
          )}
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === "keys" && (
        <div className="space-y-4">
          <Button
            size="sm"
            onClick={() =>
              createKeyMutation.mutate({
                name: `Key ${keys.length + 1}`,
                scopes: [],
              })
            }
            disabled={createKeyMutation.isPending}
          >
            + Generate API Key
          </Button>

          {keys.length === 0 ? (
            <p className="py-8 text-center text-gray-500 dark:text-gray-400">No API keys yet.</p>
          ) : (
            <div className="space-y-3">
              {keys.map((key) => (
                <div key={key.id} className="rounded-lg border p-4 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium">{key.name}</span>
                      <span className="ml-2 font-mono text-sm text-gray-500">
                        {key.key_prefix}…
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {key.last_used_at
                        ? `Last used ${new Date(key.last_used_at).toLocaleDateString()}`
                        : "Never used"}
                    </span>
                  </div>
                  {key.scopes.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {key.scopes.map((scope) => (
                        <span
                          key={scope}
                          className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700"
                        >
                          {scope}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

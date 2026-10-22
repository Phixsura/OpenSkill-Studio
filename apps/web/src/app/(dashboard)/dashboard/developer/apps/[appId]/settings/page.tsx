"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface AppDetail {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  homepage_url: string | null;
  privacy_policy_url: string | null;
  visibility: string;
  oauth_client_id: string | null;
  redirect_uris: string[] | null;
  webhook_url: string | null;
}

export default function AppSettingsPage() {
  const { appId } = useParams<{ appId: string }>();
  const queryClient = useQueryClient();

  const { data: app, isLoading } = useQuery({
    queryKey: ["developer-app", appId],
    queryFn: () =>
      apiWithAuth<{ data: AppDetail }>(`/developer/apps/${appId}`).then((r) => r.data),
  });

  const [form, setForm] = useState({
    description: "",
    homepage_url: "",
    privacy_policy_url: "",
    webhook_url: "",
    visibility: "private",
  });
  const [redirectUris, setRedirectUris] = useState("");

  useEffect(() => {
    if (app) {
      setForm({
        description: app.description ?? "",
        homepage_url: app.homepage_url ?? "",
        privacy_policy_url: app.privacy_policy_url ?? "",
        webhook_url: app.webhook_url ?? "",
        visibility: app.visibility,
      });
      setRedirectUris((app.redirect_uris ?? []).join("\n"));
    }
  }, [app]);

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      apiWithAuth(`/developer/apps/${appId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["developer-app", appId] });
    },
  });

  const handleSave = () => {
    const uris = redirectUris
      .split("\n")
      .map((u) => u.trim())
      .filter(Boolean);
    updateMutation.mutate({
      description: form.description || null,
      homepage_url: form.homepage_url || null,
      privacy_policy_url: form.privacy_policy_url || null,
      webhook_url: form.webhook_url || null,
      visibility: form.visibility,
      redirect_uris: uris,
    });
  };

  if (isLoading || !app) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold">App Settings</h1>

      <div className="space-y-6">
        {/* General */}
        <div className="rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-4 text-lg font-semibold">General</h2>
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Description</label>
              <textarea
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Visibility</label>
              <select
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.visibility}
                onChange={(e) => setForm({ ...form, visibility: e.target.value })}
              >
                <option value="private">Private — only you</option>
                <option value="unlisted">Unlisted — accessible by link</option>
                <option value="public">Public — listed in marketplace</option>
              </select>
            </div>
          </div>
        </div>

        {/* URLs */}
        <div className="rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-4 text-lg font-semibold">URLs</h2>
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Homepage URL</label>
              <input
                type="url"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.homepage_url}
                onChange={(e) => setForm({ ...form, homepage_url: e.target.value })}
                placeholder="https://your-app.example.com"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">
                Privacy Policy URL
                {form.visibility === "public" && (
                  <span className="ml-1 text-red-500">*required for public apps</span>
                )}
              </label>
              <input
                type="url"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.privacy_policy_url}
                onChange={(e) => setForm({ ...form, privacy_policy_url: e.target.value })}
                placeholder="https://your-app.example.com/privacy"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Webhook URL</label>
              <input
                type="url"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.webhook_url}
                onChange={(e) => setForm({ ...form, webhook_url: e.target.value })}
                placeholder="https://your-app.example.com/webhooks/openskill"
              />
              <p className="mt-1 text-xs text-gray-400">
                Events will be delivered via HMAC-SHA256 signed HTTP POST
              </p>
            </div>
          </div>
        </div>

        {/* OAuth */}
        <div className="rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-4 text-lg font-semibold">OAuth 2.0</h2>
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Client ID</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 rounded bg-gray-50 px-3 py-2 text-sm dark:bg-gray-800">
                  {app.oauth_client_id ?? "—"}
                </code>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    if (app.oauth_client_id) {
                      navigator.clipboard.writeText(app.oauth_client_id);
                    }
                  }}
                >
                  Copy
                </Button>
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">
                Redirect URIs (one per line)
              </label>
              <textarea
                className="w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800"
                value={redirectUris}
                onChange={(e) => setRedirectUris(e.target.value)}
                rows={4}
                placeholder={"https://your-app.example.com/callback\nhttp://localhost:3000/callback"}
              />
              <p className="mt-1 text-xs text-gray-400">
                Must use HTTPS (or http://localhost for development)
              </p>
            </div>
          </div>
        </div>

        {/* Save */}
        <div className="flex items-center gap-3">
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            {updateMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
          {updateMutation.isSuccess && (
            <span className="text-sm text-green-600">✓ Saved</span>
          )}
          {updateMutation.isError && (
            <span className="text-sm text-red-600">
              {(updateMutation.error as Error).message}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

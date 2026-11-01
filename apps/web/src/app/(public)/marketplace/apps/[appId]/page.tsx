"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";

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
  created_at: string;
  updated_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

/** Only allow http(s) URLs to prevent javascript: XSS */
function safeUrl(u: string | null | undefined): string | null {
  if (!u) return null;
  try {
    const p = new URL(u);
    return p.protocol === "https:" || p.protocol === "http:" ? p.href : null;
  } catch {
    return null;
  }
}

const CATEGORY_LABELS: Record<string, string> = {
  connector: "🔌 Connector",
  workflow_adapter: "⚡ Workflow Adapter",
  ui_extension: "🖥️ UI Extension",
  analytics: "📊 Analytics",
  automation: "🤖 Automation",
  content_pack: "📦 Content Pack",
  ecosystem_source: "🌐 Ecosystem Source",
};

export default function AppDetailPublicPage() {
  const { appId } = useParams<{ appId: string }>();
  const router = useRouter();

  const { data: app, isLoading } = useQuery({
    queryKey: ["marketplace-app", appId],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/marketplace/apps/${appId}`);
      if (!res.ok) throw new Error("App not found");
      const json = await res.json();
      return json.data as AppDetail;
    },
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <div className="space-y-4">
          <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-96 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-40 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    );
  }

  if (!app) {
    return (
      <div className="py-16 text-center">
        <h1 className="text-2xl font-bold">App Not Found</h1>
        <p className="mt-2 text-gray-500">
          This app may have been removed or is not publicly available.
        </p>
        <Button className="mt-4" onClick={() => router.push("/marketplace/apps")}>
          ← Back to Marketplace
        </Button>
      </div>
    );
  }

  const permissions = (app.manifest as Record<string, unknown>)?.permissions as
    string[] | undefined;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Back link */}
      <button
        className="mb-6 text-sm text-blue-600 hover:underline"
        onClick={() => router.push("/marketplace/apps")}
      >
        ← Back to Marketplace
      </button>

      {/* Header */}
      <div className="mb-8 flex items-start gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gray-100 text-3xl dark:bg-gray-700">
          {app.icon_url ? (
            <img src={app.icon_url} alt="" className="h-16 w-16 rounded-xl" />
          ) : (
            (CATEGORY_LABELS[app.category]?.charAt(0) ?? "📦")
          )}
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{app.name}</h1>
          <p className="mt-1 text-gray-500 dark:text-gray-400">
            {CATEGORY_LABELS[app.category] ?? app.category}
          </p>
          <div className="mt-2 flex gap-2">
            <span className="rounded-full bg-green-100 px-3 py-0.5 text-sm text-green-800 dark:bg-green-900 dark:text-green-200">
              {app.status}
            </span>
          </div>
        </div>
        <Button size="default">Install App</Button>
      </div>

      {/* Description */}
      {app.description && (
        <div className="mb-8">
          <h2 className="mb-2 text-lg font-semibold">About</h2>
          <p className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">{app.description}</p>
        </div>
      )}

      {/* Permissions */}
      {permissions && permissions.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-2 text-lg font-semibold">Permissions Requested</h2>
          <div className="flex flex-wrap gap-2">
            {permissions.map((perm) => (
              <span key={perm} className="rounded bg-gray-100 px-2.5 py-1 text-sm dark:bg-gray-700">
                {perm}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Links */}
      <div className="mb-8 grid grid-cols-2 gap-4">
        {safeUrl(app.homepage_url) && (
          <a
            href={safeUrl(app.homepage_url)!}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border p-3 text-sm transition-colors hover:border-blue-500 dark:border-gray-700"
          >
            🌐 Homepage
            <p className="mt-1 truncate text-xs text-gray-400">{app.homepage_url}</p>
          </a>
        )}
        {safeUrl(app.privacy_policy_url) && (
          <a
            href={safeUrl(app.privacy_policy_url)!}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border p-3 text-sm transition-colors hover:border-blue-500 dark:border-gray-700"
          >
            🔒 Privacy Policy
            <p className="mt-1 truncate text-xs text-gray-400">{app.privacy_policy_url}</p>
          </a>
        )}
      </div>

      {/* Metadata */}
      <div className="text-sm text-gray-400">
        <p>Published: {new Date(app.created_at).toLocaleDateString()}</p>
        <p>Last updated: {new Date(app.updated_at).toLocaleDateString()}</p>
      </div>
    </div>
  );
}

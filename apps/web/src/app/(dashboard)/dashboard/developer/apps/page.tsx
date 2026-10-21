"use client";

import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface App {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: string;
  visibility: string;
  status: string;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  testing: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  submitted: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  approved: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  deprecated: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  revoked: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const CATEGORY_LABELS: Record<string, string> = {
  connector: "🔌 Connector",
  workflow_adapter: "⚡ Workflow Adapter",
  ui_extension: "🖥️ UI Extension",
  analytics: "📊 Analytics",
  automation: "🤖 Automation",
  content_pack: "📦 Content Pack",
  ecosystem_source: "🌐 Ecosystem Source",
};

const CATEGORY_OPTIONS = [
  { value: "connector", label: "Connector" },
  { value: "workflow_adapter", label: "Workflow Adapter" },
  { value: "ui_extension", label: "UI Extension" },
  { value: "analytics", label: "Analytics" },
  { value: "automation", label: "Automation" },
  { value: "content_pack", label: "Content Pack" },
  { value: "ecosystem_source", label: "Ecosystem Source" },
];

export default function DeveloperAppsPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    category: "connector",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["developer-apps"],
    queryFn: () => apiWithAuth<{ data: App[]; meta: { total: number } }>("/developer/apps"),
  });

  const createMutation = useMutation({
    mutationFn: (data: typeof form) =>
      apiWithAuth<{ data: App }>("/developer/apps", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["developer-apps"] });
      setShowCreate(false);
      setForm({ name: "", slug: "", description: "", category: "connector" });
    },
  });

  const apps = data?.data ?? [];

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Apps</h1>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "+ New App"}
        </Button>
      </div>

      {showCreate && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMutation.mutate(form);
          }}
          className="mb-6 space-y-4 rounded-lg border p-6 dark:border-gray-700"
        >
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium">App Name</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                minLength={2}
                maxLength={100}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Slug</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.slug}
                onChange={(e) =>
                  setForm({
                    ...form,
                    slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ""),
                  })
                }
                required
                placeholder="my-app-name"
              />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Category</label>
            <select
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            >
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Description</label>
            <textarea
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? "Creating..." : "Create App"}
          </Button>
          {createMutation.isError && (
            <p className="text-sm text-red-600">{(createMutation.error as Error).message}</p>
          )}
        </form>
      )}

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : apps.length === 0 ? (
        <div className="py-12 text-center text-gray-500 dark:text-gray-400">
          <p className="mb-2 text-lg">No apps yet</p>
          <p className="text-sm">
            Create your first app to start building on the OpenSkill platform
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map((app) => (
            <Link
              key={app.id}
              href={`/dashboard/developer/apps/${app.id}`}
              className="block rounded-lg border p-4 transition-colors hover:border-blue-500 dark:border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 text-lg dark:bg-gray-700">
                    {app.icon_url ? (
                      <img src={app.icon_url} alt="" className="h-10 w-10 rounded-lg" />
                    ) : (
                      (CATEGORY_LABELS[app.category]?.charAt(0) ?? "📦")
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold">{app.name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {CATEGORY_LABELS[app.category] ?? app.category}
                      {app.description && ` · ${app.description.slice(0, 60)}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[app.status] ?? ""}`}
                  >
                    {app.status}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(app.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

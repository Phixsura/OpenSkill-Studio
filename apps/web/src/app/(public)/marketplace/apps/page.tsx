"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";

interface MarketplaceApp {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: string;
  developer_name: string | null;
  install_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

const CATEGORY_ICONS: Record<string, string> = {
  connector: "🔌",
  workflow_adapter: "⚡",
  ui_extension: "🖥️",
  analytics: "📊",
  automation: "🤖",
  content_pack: "📦",
  ecosystem_source: "🌐",
};

const CATEGORIES = [
  { value: "", label: "All Categories" },
  { value: "connector", label: "🔌 Connectors" },
  { value: "workflow_adapter", label: "⚡ Workflow Adapters" },
  { value: "ui_extension", label: "🖥️ UI Extensions" },
  { value: "analytics", label: "📊 Analytics" },
  { value: "automation", label: "🤖 Automation" },
  { value: "content_pack", label: "📦 Content Packs" },
  { value: "ecosystem_source", label: "🌐 Ecosystem Sources" },
];

export default function AppMarketplacePage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["marketplace-apps", search, category],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (search) params.set("q", search);
      if (category) params.set("category", category);
      params.set("per_page", "30");
      const res = await fetch(`${API_BASE}/api/v1/marketplace/apps?${params.toString()}`);
      return res.json() as Promise<{
        data: MarketplaceApp[];
        meta: { total: number };
      }>;
    },
  });

  const apps = data?.data ?? [];
  const total = data?.meta?.total ?? 0;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">App Marketplace</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Discover apps, connectors, and extensions for OpenSkill Studio
        </p>
      </div>

      {/* Search & Filter */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row">
        <input
          type="text"
          placeholder="Search apps..."
          className="flex-1 rounded-lg border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="rounded-lg border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
        {total} app{total !== 1 ? "s" : ""} available
      </p>

      {/* App Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-40 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : apps.length === 0 ? (
        <div className="py-16 text-center text-gray-500 dark:text-gray-400">
          <p className="text-xl">No apps found</p>
          <p className="mt-2 text-sm">
            {search ? "Try a different search term" : "Be the first to publish an app!"}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {apps.map((app) => (
            <Link
              key={app.id}
              href={`/marketplace/apps/${app.id}`}
              className="group rounded-lg border p-5 transition-all hover:border-blue-500 hover:shadow-md dark:border-gray-700"
            >
              <div className="flex items-start gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-100 text-2xl dark:bg-gray-700">
                  {app.icon_url ? (
                    <img src={app.icon_url} alt="" className="h-12 w-12 rounded-lg" />
                  ) : (
                    (CATEGORY_ICONS[app.category] ?? "📦")
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold group-hover:text-blue-600">{app.name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    by {app.developer_name ?? "Unknown"}
                  </p>
                </div>
              </div>
              {app.description && (
                <p className="mt-3 line-clamp-2 text-sm text-gray-600 dark:text-gray-300">
                  {app.description}
                </p>
              )}
              <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
                <span className="rounded bg-gray-100 px-2 py-0.5 dark:bg-gray-700">
                  {app.category.replace("_", " ")}
                </span>
                <span>
                  {app.install_count} install{app.install_count !== 1 ? "s" : ""}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

interface FeaturedApp {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: string;
  developer_name: string | null;
  install_count: number;
}

interface RecentApp {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  category: string;
  developer_name: string | null;
  created_at: string | null;
}

const CATEGORY_ICONS: Record<string, string> = {
  CONNECTOR: "🔌",
  WORKFLOW_ADAPTER: "⚡",
  UI_EXTENSION: "🖥️",
  ANALYTICS: "📊",
  AUTOMATION: "🤖",
  CONTENT_PACK: "📦",
  ECOSYSTEM_SOURCE: "🌐",
  connector: "🔌",
  workflow_adapter: "⚡",
  ui_extension: "🖥️",
  analytics: "📊",
  automation: "🤖",
  content_pack: "📦",
  ecosystem_source: "🌐",
};

export default function FeaturedAppsPage() {
  const { data: featuredData } = useQuery({
    queryKey: ["marketplace-featured"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/marketplace/featured?limit=6`);
      return res.json() as Promise<{ data: FeaturedApp[] }>;
    },
  });

  const { data: recentData } = useQuery({
    queryKey: ["marketplace-recent"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/marketplace/recent?limit=10`);
      return res.json() as Promise<{ data: RecentApp[] }>;
    },
  });

  const featured = featuredData?.data ?? [];
  const recent = recentData?.data ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Featured */}
      <section className="mb-12">
        <h1 className="mb-6 text-2xl font-bold">⭐ Featured Apps</h1>
        {featured.length === 0 ? (
          <p className="py-8 text-center text-gray-400">No featured apps yet. Be the first to publish!</p>
        ) : (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {featured.map((app) => (
              <Link
                key={app.id}
                href={`/marketplace/apps/${app.id}`}
                className="group rounded-xl border p-6 transition-all hover:border-blue-500 hover:shadow-lg dark:border-gray-700"
              >
                <div className="mb-3 flex items-center gap-3">
                  <span className="text-3xl">{CATEGORY_ICONS[app.category] ?? "📦"}</span>
                  <div>
                    <h3 className="font-semibold group-hover:text-blue-600">{app.name}</h3>
                    <p className="text-xs text-gray-500">{app.developer_name ?? "Unknown"}</p>
                  </div>
                </div>
                {app.description && (
                  <p className="mb-3 text-sm text-gray-600 line-clamp-2 dark:text-gray-300">
                    {app.description}
                  </p>
                )}
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{app.category.replace("_", " ")}</span>
                  <span>{app.install_count} installs</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Recent */}
      <section>
        <h2 className="mb-4 text-xl font-bold">🆕 Recently Published</h2>
        {recent.length === 0 ? (
          <p className="py-8 text-center text-gray-400">No recent apps.</p>
        ) : (
          <div className="space-y-3">
            {recent.map((app) => (
              <Link
                key={app.id}
                href={`/marketplace/apps/${app.id}`}
                className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:border-blue-500 dark:border-gray-700"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{CATEGORY_ICONS[app.category] ?? "📦"}</span>
                  <div>
                    <h3 className="font-medium">{app.name}</h3>
                    <p className="text-xs text-gray-500">
                      by {app.developer_name ?? "Unknown"}
                      {app.description && ` · ${app.description.slice(0, 60)}`}
                    </p>
                  </div>
                </div>
                {app.created_at && (
                  <span className="text-xs text-gray-400">
                    {new Date(app.created_at).toLocaleDateString()}
                  </span>
                )}
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

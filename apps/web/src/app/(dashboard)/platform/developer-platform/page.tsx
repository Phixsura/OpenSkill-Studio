"use client";

import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface PlatformStats {
  developer_accounts: number;
  total_apps: number;
  apps_by_status: Record<string, number>;
  active_installations: number;
  executions_24h: {
    total: number;
    failed: number;
    error_rate_pct: number;
  };
}

const STATUS_COLORS: Record<string, string> = {
  DRAFT: "bg-yellow-100 text-yellow-800",
  TESTING: "bg-blue-100 text-blue-800",
  SUBMITTED: "bg-purple-100 text-purple-800",
  APPROVED: "bg-cyan-100 text-cyan-800",
  PUBLISHED: "bg-green-100 text-green-800",
  DEPRECATED: "bg-orange-100 text-orange-800",
  REVOKED: "bg-red-100 text-red-800",
};

export default function PlatformDeveloperDashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["platform-dev-stats"],
    queryFn: () =>
      apiWithAuth<{ data: PlatformStats }>("/admin/developer-platform/stats").then(
        (r) => r.data,
      ),
  });

  if (isLoading || !stats) {
    return (
      <div className="p-8">
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="mb-6 text-2xl font-bold">Developer Platform Overview</h1>

      {/* Top-level stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <div className="rounded-lg border p-5 dark:border-gray-700">
          <p className="text-sm text-gray-500">Developer Accounts</p>
          <p className="mt-1 text-3xl font-bold">{stats.developer_accounts}</p>
        </div>
        <div className="rounded-lg border p-5 dark:border-gray-700">
          <p className="text-sm text-gray-500">Total Apps</p>
          <p className="mt-1 text-3xl font-bold">{stats.total_apps}</p>
        </div>
        <div className="rounded-lg border p-5 dark:border-gray-700">
          <p className="text-sm text-gray-500">Active Installations</p>
          <p className="mt-1 text-3xl font-bold">{stats.active_installations}</p>
        </div>
        <div className="rounded-lg border p-5 dark:border-gray-700">
          <p className="text-sm text-gray-500">Executions (24h)</p>
          <p className="mt-1 text-3xl font-bold">{stats.executions_24h.total}</p>
          {stats.executions_24h.failed > 0 && (
            <p className="text-xs text-red-500">
              {stats.executions_24h.failed} failed ({stats.executions_24h.error_rate_pct}%)
            </p>
          )}
        </div>
      </div>

      {/* Apps by status */}
      <div className="mb-8 rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-4 text-lg font-semibold">Apps by Status</h2>
        <div className="flex flex-wrap gap-3">
          {Object.entries(stats.apps_by_status).map(([status, count]) => (
            <div
              key={status}
              className={`rounded-lg px-4 py-2 ${STATUS_COLORS[status] ?? "bg-gray-100 text-gray-800"}`}
            >
              <span className="text-sm font-medium">{status}</span>
              <span className="ml-2 text-lg font-bold">{count}</span>
            </div>
          ))}
          {Object.keys(stats.apps_by_status).length === 0 && (
            <p className="text-sm text-gray-400">No apps yet</p>
          )}
        </div>
      </div>

      {/* Health indicators */}
      <div className="rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-4 text-lg font-semibold">Platform Health</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-500">Execution Error Rate</p>
            <p
              className={`text-2xl font-bold ${
                stats.executions_24h.error_rate_pct > 10
                  ? "text-red-600"
                  : stats.executions_24h.error_rate_pct > 5
                    ? "text-yellow-600"
                    : "text-green-600"
              }`}
            >
              {stats.executions_24h.error_rate_pct}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Published Apps</p>
            <p className="text-2xl font-bold">
              {stats.apps_by_status.PUBLISHED ?? 0}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Pending Reviews</p>
            <p className="text-2xl font-bold text-purple-600">
              {stats.apps_by_status.SUBMITTED ?? 0}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

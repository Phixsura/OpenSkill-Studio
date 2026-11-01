"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface HealthData {
  app_id: string;
  status: string;
  message: string;
  executions_24h: {
    total: number;
    failed: number;
    error_rate_pct: number;
  };
  version_adoption: Array<{
    version: string;
    version_id: string;
    install_count: number;
    adoption_pct: number;
  }>;
}

const STATUS_CONFIG: Record<string, { color: string; icon: string; bg: string }> = {
  healthy: { color: "text-green-600", icon: "✅", bg: "bg-green-50 dark:bg-green-900/20" },
  degraded: { color: "text-yellow-600", icon: "⚠️", bg: "bg-yellow-50 dark:bg-yellow-900/20" },
  critical: { color: "text-red-600", icon: "🔴", bg: "bg-red-50 dark:bg-red-900/20" },
  unknown: { color: "text-gray-500", icon: "❓", bg: "bg-gray-50 dark:bg-gray-800" },
};

export default function AppHealthPage() {
  const { appId } = useParams<{ appId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["app-health", appId],
    queryFn: () =>
      apiWithAuth<{ data: HealthData }>(`/developer/apps/${appId}/health`).then((r) => r.data),
    refetchInterval: 60_000, // Auto-refresh every minute
  });

  if (isLoading || !data) {
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

  const config = STATUS_CONFIG[data.status] ?? { color: "text-gray-500", icon: "❓", bg: "bg-gray-50 dark:bg-gray-800" };

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold">App Health</h1>

      {/* Status banner */}
      <div className={`mb-8 rounded-xl p-6 ${config.bg}`}>
        <div className="flex items-center gap-4">
          <span className="text-4xl">{config.icon}</span>
          <div>
            <h2 className={`text-xl font-bold ${config.color}`}>
              {data.status.charAt(0).toUpperCase() + data.status.slice(1)}
            </h2>
            <p className="mt-1 text-gray-600 dark:text-gray-400">{data.message}</p>
          </div>
        </div>
      </div>

      {/* Execution metrics */}
      <div className="mb-8">
        <h3 className="mb-4 text-lg font-semibold">Execution Metrics (24h)</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg border p-5 text-center dark:border-gray-700">
            <p className="text-3xl font-bold">{data.executions_24h.total}</p>
            <p className="mt-1 text-sm text-gray-500">Total Executions</p>
          </div>
          <div className="rounded-lg border p-5 text-center dark:border-gray-700">
            <p className="text-3xl font-bold text-red-600">{data.executions_24h.failed}</p>
            <p className="mt-1 text-sm text-gray-500">Failed</p>
          </div>
          <div className="rounded-lg border p-5 text-center dark:border-gray-700">
            <p
              className={`text-3xl font-bold ${
                data.executions_24h.error_rate_pct > 20
                  ? "text-red-600"
                  : data.executions_24h.error_rate_pct > 5
                    ? "text-yellow-600"
                    : "text-green-600"
              }`}
            >
              {data.executions_24h.error_rate_pct}%
            </p>
            <p className="mt-1 text-sm text-gray-500">Error Rate</p>
          </div>
        </div>
      </div>

      {/* Version Adoption */}
      <div>
        <h3 className="mb-4 text-lg font-semibold">Version Adoption</h3>
        {data.version_adoption.length === 0 ? (
          <p className="py-4 text-center text-sm text-gray-400">No versions published</p>
        ) : (
          <div className="space-y-3">
            {data.version_adoption.map((v) => (
              <div key={v.version_id} className="rounded-lg border p-4 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-semibold">v{v.version}</span>
                  <span className="text-sm text-gray-500">
                    {v.install_count} install{v.install_count !== 1 ? "s" : ""}
                  </span>
                </div>
                {/* Progress bar */}
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${Math.max(v.adoption_pct, 2)}%` }}
                  />
                </div>
                <p className="mt-1 text-right text-xs text-gray-400">{v.adoption_pct}%</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

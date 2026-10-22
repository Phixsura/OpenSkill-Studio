"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

export default function AppMetricsPage() {
  const { appId } = useParams<{ appId: string }>();

  const { data: stats } = useQuery({
    queryKey: ["app-stats", appId],
    queryFn: () =>
      apiWithAuth<{ data: Record<string, unknown> }>(`/developer/apps/${appId}/stats`).then(
        (r) => r.data,
      ),
    refetchInterval: 30_000,
  });

  const { data: health } = useQuery({
    queryKey: ["app-health", appId],
    queryFn: () =>
      apiWithAuth<{ data: Record<string, unknown> }>(`/developer/apps/${appId}/health`).then(
        (r) => r.data,
      ),
    refetchInterval: 60_000,
  });

  const { data: usage } = useQuery({
    queryKey: ["app-usage", appId],
    queryFn: () =>
      apiWithAuth<{ data: Record<string, unknown> }>(`/developer/apps/${appId}/usage`).then(
        (r) => r.data,
      ),
  });

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold">Metrics & Monitoring</h1>

      {/* Real-time stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Active Installs" value={stats?.active_installs as number ?? 0} />
        <StatCard label="Total Installs" value={stats?.total_installs as number ?? 0} />
        <StatCard label="Versions" value={stats?.versions as number ?? 0} />
        <StatCard label="API Keys" value={stats?.active_api_keys as number ?? 0} />
      </div>

      {/* Health */}
      {health && (
        <div className="mb-8 rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-3 text-lg font-semibold">Health Status</h2>
          <div className="flex items-center gap-3">
            <span className="text-2xl">
              {health.status === "healthy" ? "🟢" : health.status === "degraded" ? "🟡" : health.status === "critical" ? "🔴" : "⚪"}
            </span>
            <div>
              <p className="font-medium">{String(health.status).charAt(0).toUpperCase() + String(health.status).slice(1)}</p>
              <p className="text-sm text-gray-500">{health.message as string}</p>
            </div>
          </div>
        </div>
      )}

      {/* Usage */}
      {usage && (
        <div className="rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-3 text-lg font-semibold">Usage Summary</h2>
          <pre className="rounded bg-gray-50 p-3 text-xs dark:bg-gray-800">
            {JSON.stringify(usage, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border p-4 text-center dark:border-gray-700">
      <p className="text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-gray-500">{label}</p>
    </div>
  );
}

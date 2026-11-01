"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface OrgAppStats {
  org_id: string;
  installed_apps: number;
  executions_24h: {
    total: number;
    failed: number;
    avg_duration_ms: number;
  };
}

export default function OrgAppStatsPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data: stats, isLoading } = useQuery({
    queryKey: ["org-app-stats", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OrgAppStats }>(`/orgs/${orgId}/apps/stats`).then((r) => r.data),
    refetchInterval: 60_000,
  });

  if (isLoading || !stats) {
    return (
      <div className="p-8">
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold">App Usage Overview</h1>

      <div className="mb-8 grid grid-cols-3 gap-4">
        <div className="rounded-lg border p-5 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{stats.installed_apps}</p>
          <p className="mt-1 text-sm text-gray-500">Installed Apps</p>
        </div>
        <div className="rounded-lg border p-5 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{stats.executions_24h.total}</p>
          <p className="mt-1 text-sm text-gray-500">Executions (24h)</p>
        </div>
        <div className="rounded-lg border p-5 text-center dark:border-gray-700">
          <p className={`text-3xl font-bold ${stats.executions_24h.failed > 0 ? "text-red-600" : "text-green-600"}`}>
            {stats.executions_24h.failed}
          </p>
          <p className="mt-1 text-sm text-gray-500">Failed (24h)</p>
        </div>
      </div>

      {stats.executions_24h.total > 0 && (
        <div className="rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-3 text-lg font-semibold">Performance</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Average execution duration:{" "}
            <span className="font-bold">{stats.executions_24h.avg_duration_ms.toFixed(0)}ms</span>
          </p>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Error rate:{" "}
            <span className="font-bold">
              {stats.executions_24h.total > 0
                ? ((stats.executions_24h.failed / stats.executions_24h.total) * 100).toFixed(1)
                : 0}
              %
            </span>
          </p>
        </div>
      )}
    </div>
  );
}

"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface AnalyticsSummary {
  app_id: string;
  active_installs: number;
  installs_this_week: number;
  versions: number;
  executions_24h: number;
  executions_this_week: number;
}

interface InstallTimeline {
  timeline: Array<{ date: string; installs: number; uninstalls: number }>;
}

export default function AppAnalyticsPage() {
  const { appId } = useParams<{ appId: string }>();

  const { data: summary } = useQuery({
    queryKey: ["app-analytics-summary", appId],
    queryFn: () =>
      apiWithAuth<{ data: AnalyticsSummary }>(
        `/developer/apps/${appId}/analytics/summary`,
      ).then((r) => r.data),
    refetchInterval: 60_000,
  });

  const { data: installData } = useQuery({
    queryKey: ["app-analytics-installs", appId],
    queryFn: () =>
      apiWithAuth<{ data: InstallTimeline }>(
        `/developer/apps/${appId}/analytics/installs?days=30`,
      ).then((r) => r.data),
  });

  const timeline = installData?.timeline ?? [];

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold">Analytics</h1>

      {/* Summary cards */}
      {summary && (
        <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-5">
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Active Installs</p>
            <p className="mt-1 text-2xl font-bold">{summary.active_installs}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Installs (7d)</p>
            <p className="mt-1 text-2xl font-bold text-green-600">
              +{summary.installs_this_week}
            </p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Versions</p>
            <p className="mt-1 text-2xl font-bold">{summary.versions}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Exec (24h)</p>
            <p className="mt-1 text-2xl font-bold">{summary.executions_24h}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Exec (7d)</p>
            <p className="mt-1 text-2xl font-bold">{summary.executions_this_week}</p>
          </div>
        </div>
      )}

      {/* Install timeline */}
      <div className="mb-8 rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-4 text-lg font-semibold">Install Trend (30 days)</h2>
        {timeline.length === 0 ? (
          <p className="py-4 text-center text-sm text-gray-400">No install data yet</p>
        ) : (
          <div className="space-y-1">
            {timeline.map((day) => {
              const maxVal = Math.max(...timeline.map((d) => d.installs + d.uninstalls), 1);
              const barWidth = Math.max(((day.installs + day.uninstalls) / maxVal) * 100, 2);
              return (
                <div key={day.date} className="flex items-center gap-3 text-xs">
                  <span className="w-20 text-gray-400">{day.date.slice(5)}</span>
                  <div className="flex-1">
                    <div className="flex h-4 overflow-hidden rounded">
                      {day.installs > 0 && (
                        <div
                          className="bg-green-500"
                          style={{
                            width: `${(day.installs / maxVal) * 100}%`,
                          }}
                          title={`${day.installs} installs`}
                        />
                      )}
                      {day.uninstalls > 0 && (
                        <div
                          className="bg-red-400"
                          style={{
                            width: `${(day.uninstalls / maxVal) * 100}%`,
                          }}
                          title={`${day.uninstalls} uninstalls`}
                        />
                      )}
                    </div>
                  </div>
                  <span className="w-16 text-right text-gray-500">
                    +{day.installs} / -{day.uninstalls}
                  </span>
                </div>
              );
            })}
            <div className="mt-2 flex gap-4 text-xs text-gray-400">
              <span>
                <span className="mr-1 inline-block h-2 w-2 rounded bg-green-500" /> Installs
              </span>
              <span>
                <span className="mr-1 inline-block h-2 w-2 rounded bg-red-400" /> Uninstalls
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

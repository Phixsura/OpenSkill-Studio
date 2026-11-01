"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { apiWithAuth } from "@/lib/api";

interface SandboxExecution {
  id: string;
  installation_id: string;
  app_version_id: string;
  function_name: string;
  trigger_type: string;
  trigger_event: string | null;
  status: string;
  duration_ms: number | null;
  memory_peak_mb: number | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  running: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  timeout: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  cancelled: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export default function AppEventsPage() {
  const { appId } = useParams<{ appId: string }>();
  const [selectedExec, setSelectedExec] = useState<SandboxExecution | null>(null);

  // Get app stats to find installations
  const { data: statsData } = useQuery({
    queryKey: ["app-stats", appId],
    queryFn: () =>
      apiWithAuth<{ data: { active_installs: number; executions_24h: Record<string, number> } }>(
        `/developer/apps/${appId}/stats`,
      ).then((r) => r.data),
  });

  const stats = statsData;

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-2 text-2xl font-bold">Events & Executions</h1>
      <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
        Monitor webhook deliveries and sandbox executions for your app
      </p>

      {/* Summary cards */}
      {stats && (
        <div className="mb-6 grid grid-cols-4 gap-4">
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Total (24h)</p>
            <p className="text-xl font-bold">{stats.executions_24h?.total ?? 0}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Completed</p>
            <p className="text-xl font-bold text-green-600">
              {stats.executions_24h?.completed ?? 0}
            </p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Failed</p>
            <p className="text-xl font-bold text-red-600">
              {stats.executions_24h?.failed ?? 0}
            </p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Timeout</p>
            <p className="text-xl font-bold text-orange-600">
              {stats.executions_24h?.timeout ?? 0}
            </p>
          </div>
        </div>
      )}

      {/* Performance metrics */}
      {stats && (stats.executions_24h?.total ?? 0) > 0 && (
        <div className="mb-6 rounded-lg border p-4 dark:border-gray-700">
          <h3 className="mb-2 text-sm font-semibold text-gray-500">Performance (24h)</h3>
          <div className="flex gap-8 text-sm">
            <div>
              <span className="text-gray-400">Avg Duration: </span>
              <span className="font-medium">
                {(stats.executions_24h?.avg_duration_ms ?? 0).toFixed(0)}ms
              </span>
            </div>
            <div>
              <span className="text-gray-400">Max Duration: </span>
              <span className="font-medium">
                {stats.executions_24h?.max_duration_ms ?? 0}ms
              </span>
            </div>
            <div>
              <span className="text-gray-400">Active Installs: </span>
              <span className="font-medium">{stats.active_installs ?? 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Event types reference */}
      <div className="rounded-lg border p-6 dark:border-gray-700">
        <h3 className="mb-3 text-lg font-semibold">Subscribable Event Types</h3>
        <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
          Events your app can subscribe to via the installation&apos;s event subscription API
        </p>
        <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-3">
          {[
            "submission.completed",
            "submission.graded",
            "cohort.member_added",
            "cohort.member_removed",
            "project.published",
            "pack.published",
            "pack.installed",
            "workflow.run_completed",
            "workflow.run_failed",
            "talent.credential_issued",
            "talent.application_submitted",
            "marketplace.purchase_completed",
            "evaluation.completed",
            "org.member_added",
            "app.installed",
          ].map((event) => (
            <div
              key={event}
              className="rounded bg-gray-50 px-2 py-1 font-mono text-xs dark:bg-gray-800"
            >
              {event}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

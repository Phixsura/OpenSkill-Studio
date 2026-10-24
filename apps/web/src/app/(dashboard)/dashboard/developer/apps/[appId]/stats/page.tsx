"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface AppStats {
  app_id: string;
  status: string;
  active_installs: number;
  total_installs: number;
  versions: number;
  active_api_keys: number;
  executions_24h: {
    total: number;
    completed: number;
    failed: number;
    timeout: number;
    avg_duration_ms: number;
    max_duration_ms: number;
  };
}

interface ConformanceReport {
  app_name: string;
  version: string;
  checked_at: string;
  summary: {
    passed: boolean;
    total_checks: number;
    pass: number;
    fail: number;
    warn: number;
    skip: number;
  };
  checks: Array<{
    name: string;
    status: string;
    message: string;
  }>;
}

const STATUS_ICON: Record<string, string> = {
  pass: "✅",
  fail: "❌",
  warn: "⚠️",
  skip: "⏭️",
};

export default function AppStatsPage() {
  const { appId } = useParams<{ appId: string }>();

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["app-stats", appId],
    queryFn: () =>
      apiWithAuth<{ data: AppStats }>(`/developer/apps/${appId}/stats`).then((r) => r.data),
  });

  const { data: conformance, isLoading: confLoading } = useQuery({
    queryKey: ["app-conformance", appId],
    queryFn: () =>
      apiWithAuth<{ data: ConformanceReport }>(`/developer/apps/${appId}/conformance`).then(
        (r) => r.data,
      ),
  });

  if (statsLoading || confLoading) {
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
    <div className="max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold">App Dashboard</h1>

      {/* Stats Cards */}
      {stats && (
        <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">Active Installs</p>
            <p className="mt-1 text-2xl font-bold">{stats.active_installs}</p>
            <p className="text-xs text-gray-400">{stats.total_installs} total</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">Versions</p>
            <p className="mt-1 text-2xl font-bold">{stats.versions}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">API Keys</p>
            <p className="mt-1 text-2xl font-bold">{stats.active_api_keys}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">Executions (24h)</p>
            <p className="mt-1 text-2xl font-bold">{stats.executions_24h.total}</p>
            {stats.executions_24h.failed > 0 && (
              <p className="text-xs text-red-500">{stats.executions_24h.failed} failed</p>
            )}
          </div>
        </div>
      )}

      {/* Execution Details */}
      {stats && stats.executions_24h.total > 0 && (
        <div className="mb-8 rounded-lg border p-6 dark:border-gray-700">
          <h2 className="mb-4 text-lg font-semibold">Execution Performance (24h)</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-xl font-bold text-green-600">{stats.executions_24h.completed}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg Duration</p>
              <p className="text-xl font-bold">
                {stats.executions_24h.avg_duration_ms.toFixed(0)}ms
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Max Duration</p>
              <p className="text-xl font-bold">{stats.executions_24h.max_duration_ms}ms</p>
            </div>
          </div>
        </div>
      )}

      {/* Conformance Report */}
      {conformance && (
        <div className="rounded-lg border p-6 dark:border-gray-700">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Conformance Report</h2>
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${
                conformance.summary.passed
                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
              }`}
            >
              {conformance.summary.passed ? "All Passed" : "Issues Found"}
            </span>
          </div>

          <div className="mb-4 flex gap-4 text-sm">
            <span className="text-green-600">✅ {conformance.summary.pass} pass</span>
            <span className="text-red-600">❌ {conformance.summary.fail} fail</span>
            <span className="text-yellow-600">⚠️ {conformance.summary.warn} warn</span>
            <span className="text-gray-400">⏭️ {conformance.summary.skip} skip</span>
          </div>

          <div className="space-y-2">
            {conformance.checks.map((check, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded px-3 py-2 text-sm odd:bg-gray-50 dark:odd:bg-gray-800"
              >
                <span>{STATUS_ICON[check.status] ?? "❓"}</span>
                <span className="font-medium">{check.name}</span>
                <span className="text-gray-500 dark:text-gray-400">{check.message}</span>
              </div>
            ))}
          </div>

          <p className="mt-4 text-xs text-gray-400">
            Checked: {new Date(conformance.checked_at).toLocaleString()} · Version:{" "}
            {conformance.version}
          </p>
        </div>
      )}
    </div>
  );
}

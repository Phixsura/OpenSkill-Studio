"use client";

import { useState } from "react";

interface InstallStats {
  activeInstalls: number;
  totalInstalls: number;
  totalUninstalls: number;
  updates: number;
  retentionRate: number;
  churnRate: number;
}

interface SourceBreakdown {
  source: string;
  count: number;
}

interface RegionBreakdown {
  region: string;
  count: number;
}

interface VersionAdoption {
  version: string;
  count: number;
}

export function InstallAnalyticsChart({
  stats,
  sources,
  regions,
  versions,
  extensionName,
}: {
  stats: InstallStats;
  sources: SourceBreakdown[];
  regions: RegionBreakdown[];
  versions: VersionAdoption[];
  extensionName: string;
}) {
  const [tab, setTab] = useState<"overview" | "sources" | "regions" | "versions">("overview");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📊 {extensionName} Install Analytics</h2>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Active</span>
          <span className="text-xl font-bold text-green-600">{stats.activeInstalls.toLocaleString()}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Retention</span>
          <span className="text-xl font-bold text-blue-600">{stats.retentionRate}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Churn</span>
          <span className="text-xl font-bold text-red-500">{stats.churnRate}%</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["overview", "sources", "regions", "versions"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-500">Total Installs</span><span className="font-bold">{stats.totalInstalls}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Total Uninstalls</span><span className="text-red-500">{stats.totalUninstalls}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Updates</span><span>{stats.updates}</span></div>
        </div>
      )}

      {tab === "sources" && (
        <div className="space-y-1">
          {sources.map((s) => (
            <div key={s.source} className="flex justify-between items-center rounded-lg border dark:border-gray-700 p-2 text-sm">
              <span className="capitalize">{s.source}</span>
              <span className="font-bold">{s.count}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "regions" && (
        <div className="space-y-1">
          {regions.map((r) => (
            <div key={r.region} className="flex justify-between items-center rounded-lg border dark:border-gray-700 p-2 text-sm">
              <span>{r.region}</span>
              <span className="font-bold">{r.count}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "versions" && (
        <div className="space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="flex justify-between items-center rounded-lg border dark:border-gray-700 p-2 text-sm">
              <code>{v.version}</code>
              <span className="font-bold">{v.count} users</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

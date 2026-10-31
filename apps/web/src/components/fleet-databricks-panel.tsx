"use client";
export function FleetDatabricksPanel({ workspaces, active, clusters, dbu }: { workspaces: number; active: number; clusters: number; dbu: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧱 Databricks</h3>
    <div className="text-sm">{active}/{workspaces} active · {clusters} clusters · {dbu} DBU/24h</div>
  </div>);
}

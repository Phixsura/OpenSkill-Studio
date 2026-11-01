"use client";
export function FleetGrafanaPanel({ total, active, stale, usageRate }: { total: number; active: number; stale: number; usageRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Grafana</h3>
    <div className="text-sm">{active}/{total} active ({usageRate}%)</div>
    {stale > 0 && <span className="text-xs text-yellow-600">🧹 {stale} stale dashboards</span>}
  </div>);
}

"use client";
export function FleetConnpoolPanel({ used, max, pct, saturated }: { used: number; max: number; pct: number; saturated: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 Fleet Connections</h3>
    <div className="text-sm">{used}/{max} connections ({pct}%)</div>
    {saturated && <span className="text-xs text-red-500">⚠️ Connection pool saturated</span>}
  </div>);
}

"use client";
export function FleetGwRatelimitPanel({ limited, total, limitedPct, excessive }: { limited: number; total: number; limitedPct: number; excessive: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 Gateway Rate Limits</h3>
    <div className="text-sm">{limited.toLocaleString()} / {total.toLocaleString()} limited ({limitedPct}%)</div>
    {excessive && <span className="text-xs text-yellow-600">⚠️ Excessive rate limiting</span>}
  </div>);
}

"use client";
export function FleetGraphqlPanel({ total, slowQueries, deepQueries, avgDuration, healthy }: { total: number; slowQueries: number; deepQueries: number; avgDuration: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">◆ GraphQL</h3>
    <div className="text-sm">{total} queries · avg {avgDuration}ms · {slowQueries} slow · {deepQueries} deep</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ Slow queries detected</span>}
  </div>);
}

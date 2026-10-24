"use client";
export function FleetMockSrvPanel({ total, active, hits, wellUsed }: { total: number; active: number; hits: number; wellUsed: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎭 Mock Server</h3>
    <div className="text-sm">{active}/{total} active · {hits.toLocaleString()} hits/24h</div>
    {wellUsed && <span className="text-xs text-green-600">✅ Well-utilized</span>}
  </div>);
}

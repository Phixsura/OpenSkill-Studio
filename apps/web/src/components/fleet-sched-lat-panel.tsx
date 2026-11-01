"use client";
export function FleetSchedLatPanel({ total, avgMs, slowScheduling, fast }: { total: number; avgMs: number; slowScheduling: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Scheduling Latency</h3>
    <div className="text-sm">avg {avgMs}ms · {total} pods</div>
    {!fast && <span className="text-xs text-yellow-600">⚠️ {slowScheduling} slow schedules</span>}
  </div>);
}

"use client";
export function FleetOomPanel({ total, oomPods, totalOoms, healthy }: { total: number; oomPods: number; totalOoms: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💥 OOM Kills</h3>
    {healthy ? <span className="text-xs text-green-600">✅ No OOM kills</span>
     : <span className="text-xs text-red-500">🚨 {totalOoms} OOMs across {oomPods} pods</span>}
  </div>);
}

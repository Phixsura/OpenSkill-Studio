"use client";
export function FleetLivenessPanel({ total, failingPods, totalFailures, healthy }: { total: number; failingPods: number; totalFailures: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💓 Liveness Probes</h3>
    {healthy ? <span className="text-xs text-green-600">✅ All {total} pods healthy</span>
     : <span className="text-xs text-red-500">⚠️ {failingPods} pods failing ({totalFailures} failures)</span>}
  </div>);
}

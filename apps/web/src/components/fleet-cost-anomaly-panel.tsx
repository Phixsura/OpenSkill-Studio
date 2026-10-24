"use client";
export function FleetCostAnomalyPanel({ anomaly, latest, baseline, ratio }: { anomaly: boolean; latest: number; baseline: number; ratio: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💸 Cost Anomaly</h3>
    {anomaly ? <span className="text-xs text-red-500">🚨 {ratio}x spike! ${latest} vs ${baseline} baseline</span>
     : <span className="text-xs text-green-600">✅ Normal — ${latest} (baseline ${baseline})</span>}
  </div>);
}

"use client";
export function FleetFunnelPanel({ steps, overallRate, worstDrop, healthy }: { steps: number; overallRate: number; worstDrop: { step: string; drop_pct: number } | null; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔻 Conversion Funnel</h3>
    <div className={`text-lg font-bold ${healthy ? "text-green-600" : "text-red-500"}`}>{overallRate}% conversion</div>
    {worstDrop && <div className="text-xs text-yellow-600">Worst drop: {worstDrop.step} ({worstDrop.drop_pct}%)</div>}
  </div>);
}

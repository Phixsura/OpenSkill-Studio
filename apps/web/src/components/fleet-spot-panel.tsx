"use client";
export function FleetSpotPanel({ total, spot, onDemand, spotPct, costOptimized }: { total: number; spot: number; onDemand: number; spotPct: number; costOptimized: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💲 Spot Instances</h3>
    <div className="text-sm">{spot} spot · {onDemand} on-demand ({spotPct}% spot)</div>
    <span className={`text-xs ${costOptimized ? "text-green-600" : "text-yellow-600"}`}>{costOptimized ? "✅ Cost optimized" : "💸 Could save more"}</span>
  </div>);
}

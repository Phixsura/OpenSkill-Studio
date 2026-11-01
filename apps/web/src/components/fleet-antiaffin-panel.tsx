"use client";
export function FleetAntiaffinPanel({ total, withAa, colocatedRisk, haCompliant }: { total: number; withAa: number; colocatedRisk: number; haCompliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Anti-Affinity</h3>
    <div className="text-sm">{withAa}/{total} with anti-affinity</div>
    {!haCompliant && <span className="text-xs text-red-500">⚠️ {colocatedRisk} co-location risks</span>}
  </div>);
}

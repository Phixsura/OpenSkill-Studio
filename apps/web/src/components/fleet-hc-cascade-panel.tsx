"use client";
export function FleetHcCascadePanel({ total, unhealthy, impacted, maxCascade, cascading }: { total: number; unhealthy: number; impacted: number; maxCascade: number; cascading: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Health Cascade</h3>
    <div className="text-sm">{unhealthy} unhealthy → {impacted} impacted (depth {maxCascade})</div>
    {cascading && <span className="text-xs text-red-500">🚨 Cascading failure!</span>}
  </div>);
}

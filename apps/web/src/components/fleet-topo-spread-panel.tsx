"use client";
export function FleetTopoSpreadPanel({ total, wellSpread, singleZone, resilient }: { total: number; wellSpread: number; singleZone: number; resilient: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Topology Spread</h3>
    <div className="text-sm">{wellSpread} multi-zone · {singleZone} single-zone</div>
    {!resilient && <span className="text-xs text-yellow-600">⚠️ {singleZone} single-zone deployments</span>}
  </div>);
}

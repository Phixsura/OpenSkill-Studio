"use client";
export function FleetNodepoolPanel({ pools, totalNodes, capacity, utilPct, atMax }: { pools: number; totalNodes: number; capacity: number; utilPct: number; atMax: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ Node Pools</h3>
    <div className="text-sm">{totalNodes}/{capacity} nodes ({utilPct}%) · {pools} pools</div>
    {atMax > 0 && <span className="text-xs text-yellow-600">⚠️ {atMax} pools at max</span>}
  </div>);
}

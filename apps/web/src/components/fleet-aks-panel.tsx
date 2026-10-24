"use client";
export function FleetAksPanel({ clusters, running, nodes, upgradesAvailable }: { clusters: number; running: number; nodes: number; upgradesAvailable: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ AKS</h3>
    <div className="text-sm">{running}/{clusters} running · {nodes} nodes</div>
    {upgradesAvailable > 0 && <span className="text-xs text-blue-500">⬆️ {upgradesAvailable} upgrades available</span>}
  </div>);
}

"use client";
export function FleetCalicoPanel({ nodes, healthy, totalPolicies, allHealthy }: { nodes: number; healthy: number; totalPolicies: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐯 Calico</h3>
    <div className="text-sm">{healthy}/{nodes} healthy · {totalPolicies} network policies</div>
  </div>);
}

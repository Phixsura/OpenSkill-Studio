"use client";
export function FleetRedshiftPanel({ clusters, available, nodes, storagePct }: { clusters: number; available: number; nodes: number; storagePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔴 Redshift</h3>
    <div className="text-sm">{available}/{clusters} available · {nodes} nodes · {storagePct}% storage</div>
  </div>);
}

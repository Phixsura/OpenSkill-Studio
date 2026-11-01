"use client";
export function FleetPodDisruptionV9Panel({ pdbs, disruptions }: { pdbs: number; disruptions: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛑 Pod Disruption v9</h3>
    <div className="text-sm">{pdbs} PDBs · {disruptions} disruptions today</div>
  </div>);
}

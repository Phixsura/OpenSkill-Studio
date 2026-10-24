"use client";
export function FleetDagsterPanel({ deployments, running, assets, materializations }: { deployments: number; running: number; assets: number; materializations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗡️ Dagster</h3>
    <div className="text-sm">{running}/{deployments} running · {assets} assets · {materializations.toLocaleString()} mats/24h</div>
  </div>);
}

"use client";
export function FleetModelRegPanel({ registries, models, versions, deployed, deploymentRate }: { registries: number; models: number; versions: number; deployed: number; deploymentRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Model Registry</h3>
    <div className="text-sm">{registries} registries · {models} models · {versions} versions · {deployed} deployed ({deploymentRate}%)</div>
  </div>);
}

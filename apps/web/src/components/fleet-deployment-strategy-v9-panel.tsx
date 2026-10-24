"use client";
export function FleetDeploymentStrategyV9Panel({ deployments, rolling }: { deployments: number; rolling: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Deploy Strategy v9</h3>
    <div className="text-sm">{deployments} deployments · {rolling} rolling</div>
  </div>);
}

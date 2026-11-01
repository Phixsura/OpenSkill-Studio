"use client";
export function FleetAiDeployOrchPanel({ orchestrators, active, deployments, rollbackRate, deployMin }: { orchestrators: number; active: number; deployments: number; rollbackRate: number; deployMin: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Deploy Orchestrator</h3>
    <div className="text-sm">{active}/{orchestrators} active · {deployments} deploys · {rollbackRate}% rollback · {deployMin}m avg</div>
  </div>);
}

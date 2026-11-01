"use client";
export function FleetAiDeployV4Panel({ deployers, active, deployments, rollbacks, leadTime }: { deployers: number; active: number; deployments: number; rollbacks: number; leadTime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Deployment v4</h3>
    <div className="text-sm">{active}/{deployers} active · {deployments} deploys · {rollbacks} rollbacks · {leadTime}m lead time</div>
  </div>);
}

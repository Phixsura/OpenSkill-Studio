"use client";
export function FleetAiDeployPanel({ pipelines, active, deployments, rollbacks, reliable }: { pipelines: number; active: number; deployments: number; rollbacks: number; reliable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Deploy</h3>
    <div className="text-sm">{active}/{pipelines} active · {deployments} deploys · {rollbacks} rollbacks</div>
    {reliable && <span className="text-xs text-green-600">✅ Zero rollbacks</span>}
  </div>);
}

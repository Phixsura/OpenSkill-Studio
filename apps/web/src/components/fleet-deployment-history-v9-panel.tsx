"use client";
export function FleetDeploymentHistoryV9Panel({ deploys, rollbacks }: { deploys: number; rollbacks: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 Deployment History v9</h3>
    <div className="text-sm">{deploys} deploys · {rollbacks} rollbacks</div>
  </div>);
}

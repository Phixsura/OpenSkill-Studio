"use client";
export function FleetDeploymentAuditV9Panel({ deploys, approved }: { deploys: number; approved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 Deploy Audit v9</h3>
    <div className="text-sm">{deploys} deploys · {approved} approved</div>
  </div>);
}

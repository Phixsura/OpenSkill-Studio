"use client";
export function FleetCanaryDeployV9Panel({ total, promoted }: { total: number; promoted: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐤 Canary Deploy v9</h3>
    <div className="text-sm">{total} deploys · {promoted} promoted</div>
  </div>);
}

"use client";
export function FleetBlueGreenV9Panel({ activeEnv, total }: { activeEnv: string; total: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵🟢 Blue-Green v9</h3>
    <div className="text-sm">Active: {activeEnv} · {total} deployments</div>
  </div>);
}

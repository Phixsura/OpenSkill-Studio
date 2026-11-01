"use client";
export function FleetPodLifecycleV9Panel({ pods, running }: { pods: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Pod Lifecycle v9</h3>
    <div className="text-sm">{pods} pods · {running} running</div>
  </div>);
}

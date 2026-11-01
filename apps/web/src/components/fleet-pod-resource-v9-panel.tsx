"use client";
export function FleetPodResourceV9Panel({ pods, cpuUsed }: { pods: number; cpuUsed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Pod Resource v9</h3>
    <div className="text-sm">{pods} pods · {cpuUsed}m CPU used</div>
  </div>);
}

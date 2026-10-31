"use client";
export function FleetRayServePanel({ deployments, running, replicas, qps }: { deployments: number; running: number; replicas: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔆 Ray Serve</h3>
    <div className="text-sm">{running}/{deployments} running · {replicas} replicas · {qps.toLocaleString()} qps</div>
  </div>);
}

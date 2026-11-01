"use client";
export function FleetGkePanel({ clusters, running, pods, autopilot }: { clusters: number; running: number; pods: number; autopilot: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ GKE</h3>
    <div className="text-sm">{running}/{clusters} running · {pods} pods · {autopilot} autopilot</div>
  </div>);
}

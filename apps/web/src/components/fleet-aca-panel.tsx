"use client";
export function FleetAcaPanel({ apps, running, replicas, revisions }: { apps: number; running: number; replicas: number; revisions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Container Apps</h3>
    <div className="text-sm">{running}/{apps} running · {replicas} replicas · {revisions} revisions</div>
  </div>);
}

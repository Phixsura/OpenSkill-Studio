"use client";
export function FleetApprunnerPanel({ services, running, instances, requests }: { services: number; running: number; instances: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏃 App Runner</h3>
    <div className="text-sm">{running}/{services} running · {instances} instances · {requests.toLocaleString()} req</div>
  </div>);
}

"use client";
export function FleetKservePanel({ services, ready, models, qps }: { services: number; ready: number; models: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 KServe</h3>
    <div className="text-sm">{ready}/{services} ready · {models} models · {qps.toLocaleString()} qps</div>
  </div>);
}

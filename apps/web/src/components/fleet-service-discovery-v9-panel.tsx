"use client";
export function FleetServiceDiscoveryV9Panel({ services, endpoints }: { services: number; endpoints: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Service Discovery v9</h3>
    <div className="text-sm">{services} services · {endpoints} endpoints</div>
  </div>);
}

"use client";
export function FleetConsulPanel({ datacenters, healthy, services, kvKeys }: { datacenters: number; healthy: number; services: number; kvKeys: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏛️ Consul</h3>
    <div className="text-sm">{healthy}/{datacenters} DCs · {services} services · {kvKeys.toLocaleString()} KV keys</div>
  </div>);
}

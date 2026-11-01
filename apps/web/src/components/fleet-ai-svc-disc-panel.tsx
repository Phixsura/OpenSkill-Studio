"use client";
export function FleetAiSvcDiscPanel({ registries, active, services, instances, lookups }: { registries: number; active: number; services: number; instances: number; lookups: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Service Discovery</h3>
    <div className="text-sm">{active}/{registries} active · {services} services · {instances} instances · {lookups.toLocaleString()} lookups</div>
  </div>);
}

"use client";
export function FleetServiceRegistryV9Panel({ services, instances }: { services: number; instances: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 Service Registry v9</h3>
    <div className="text-sm">{services} services · {instances} instances</div>
  </div>);
}

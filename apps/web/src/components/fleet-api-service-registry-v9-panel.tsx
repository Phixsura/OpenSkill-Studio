"use client";
export function FleetApiServiceRegistryV9Panel({ services, healthy }: { services: number; healthy: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 API Service Registry v9</h3>
    <div className="text-sm">{services} services · {healthy} healthy</div>
  </div>);
}

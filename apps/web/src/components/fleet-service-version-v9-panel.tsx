"use client";
export function FleetServiceVersionV9Panel({ services, latest }: { services: number; latest: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 Service Version v9</h3>
    <div className="text-sm">{services} services · {latest} on latest</div>
  </div>);
}

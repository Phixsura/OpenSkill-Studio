"use client";
export function FleetServiceMeshV9Panel({ services, rps }: { services: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Service Mesh v9</h3>
    <div className="text-sm">{services} services · {rps.toLocaleString()} rps</div>
  </div>);
}

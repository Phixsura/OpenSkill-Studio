"use client";
export function FleetSvcMapPanel({ services, internal, external, connections, avgConn }: { services: number; internal: number; external: number; connections: number; avgConn: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Service Map</h3>
    <div className="text-sm">{services} services · {internal} internal · {external} external · {connections} connections</div>
  </div>);
}

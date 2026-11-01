"use client";
export function FleetServiceMapV9Panel({ services, connections }: { services: number; connections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Service Map v9</h3>
    <div className="text-sm">{services} services · {connections} connections</div>
  </div>);
}

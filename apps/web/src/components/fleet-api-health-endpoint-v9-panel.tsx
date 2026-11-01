"use client";
export function FleetApiHealthEndpointV9Panel({ services, health }: { services: number; health: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 Health Endpoint v9</h3>
    <div className="text-sm">{services} services · {health} with /health</div>
  </div>);
}

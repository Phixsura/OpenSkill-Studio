"use client";
export function FleetEndpointDiscoveryV9Panel({ endpoints, discovered }: { endpoints: number; discovered: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Endpoint Discovery v9</h3>
    <div className="text-sm">{endpoints} endpoints · {discovered} auto-discovered</div>
  </div>);
}

"use client";
export function FleetServiceEndpointV9Panel({ endpoints, ready }: { endpoints: number; ready: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Service Endpoint v9</h3>
    <div className="text-sm">{endpoints} endpoints · {ready} ready</div>
  </div>);
}

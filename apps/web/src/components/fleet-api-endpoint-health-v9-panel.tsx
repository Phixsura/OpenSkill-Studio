"use client";
export function FleetApiEndpointHealthV9Panel({ endpoints, score }: { endpoints: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 Endpoint Health v9</h3>
    <div className="text-sm">{endpoints} endpoints · {score}/100 avg</div>
  </div>);
}

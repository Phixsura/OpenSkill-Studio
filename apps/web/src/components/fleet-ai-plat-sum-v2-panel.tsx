"use client";
export function FleetAiPlatSumV2Panel({ services, healthy, requests, uptime, cost, status }: { services: number; healthy: number; requests: number; uptime: number; cost: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Platform Summary v2</h3>
    <div className="text-sm">{healthy}/{services} healthy · {requests.toLocaleString()} req · {uptime}% · ${cost.toLocaleString()}</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}

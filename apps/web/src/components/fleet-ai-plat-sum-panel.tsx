"use client";
export function FleetAiPlatSumPanel({ services, healthy, requests, uptime, status }: { services: number; healthy: number; requests: number; uptime: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Platform Summary</h3>
    <div className="text-sm">{healthy}/{services} healthy · {requests.toLocaleString()} req · {uptime}% uptime</div>
    <div className="text-xs mt-1">{status}</div>
  </div>);
}

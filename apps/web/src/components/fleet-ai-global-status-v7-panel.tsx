"use client";
export function FleetAiGlobalStatusV7Panel({ regions, active, services, healthy, requests, uptime, status }: { regions: number; active: number; services: number; healthy: number; requests: number; uptime: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Global Status v7</h3>
    <div className="text-sm">{active}/{regions} regions · {healthy}/{services} healthy · {requests.toLocaleString()} req · {uptime}%</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}

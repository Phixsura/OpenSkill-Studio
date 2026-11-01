"use client";
export function FleetAiPlatOverviewPanel({ services, healthy, models, requests, uptime, revenue, status }: { services: number; healthy: number; models: number; requests: number; uptime: number; revenue: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Platform Overview</h3>
    <div className="text-sm">{healthy}/{services} healthy · {models} models · {requests.toLocaleString()} req · {uptime}% · ${revenue.toLocaleString()}</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}

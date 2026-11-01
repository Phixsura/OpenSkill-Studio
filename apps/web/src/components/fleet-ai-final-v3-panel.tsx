"use client";
export function FleetAiFinalV3Panel({ total, operational, uptime, requests, models, status }: { total: number; operational: number; uptime: number; requests: number; models: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Final Status v3</h3>
    <div className="text-sm">{operational}/{total} operational · {uptime}% uptime · {requests.toLocaleString()} req · {models} models</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}

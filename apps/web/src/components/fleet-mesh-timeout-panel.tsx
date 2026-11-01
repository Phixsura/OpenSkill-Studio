"use client";
export function FleetMeshTimeoutPanel({ requests, timeouts, timeoutRate, problematic }: { requests: number; timeouts: number; timeoutRate: number; problematic: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Mesh Timeouts</h3>
    <div className="text-sm">{timeouts} timeouts / {requests.toLocaleString()} req ({timeoutRate}%)</div>
    {problematic && <span className="text-xs text-red-500">⚠️ High timeout rate</span>}
  </div>);
}

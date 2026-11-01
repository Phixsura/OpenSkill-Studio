"use client";
export function FleetReqConcPanel({ totalConc, capacity, utilPct, pressure }: { totalConc: number; capacity: number; utilPct: number; pressure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Request Concurrency</h3>
    <div className="text-sm">{totalConc}/{capacity} ({utilPct}%)</div>
    {pressure && <span className="text-xs text-red-500">⚠️ High concurrency pressure</span>}
  </div>);
}

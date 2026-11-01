"use client";
export function FleetCfWorkersPanel({ workers, active, requests, errors, avgCpu }: { workers: number; active: number; requests: number; errors: number; avgCpu: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ CF Workers</h3>
    <div className="text-sm">{active}/{workers} active · {requests.toLocaleString()} req · {avgCpu}ms CPU</div>
    {errors > 0 && <span className="text-xs text-red-500">⚠️ {errors} errors</span>}
  </div>);
}

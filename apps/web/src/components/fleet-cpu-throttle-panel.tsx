"use client";
export function FleetCpuThrottlePanel({ total, throttled, severe, healthy }: { total: number; throttled: number; severe: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 CPU Throttling</h3>
    <div className="text-sm">{throttled}/{total} throttled</div>
    {!healthy && <span className="text-xs text-red-500">🚨 {severe} severely throttled</span>}
  </div>);
}

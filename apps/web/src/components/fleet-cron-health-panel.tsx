"use client";
export function FleetCronHealthPanel({ total, onTime, delayed, failed, healthy }: { total: number; onTime: number; delayed: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ Cron Jobs</h3>
    <div className="text-sm">{onTime} on-time · {delayed} delayed · {failed} failed</div>
    <span className={`text-xs ${healthy ? "text-green-600" : "text-yellow-600"}`}>{healthy ? "✅ All healthy" : "⚠️ Issues detected"}</span>
  </div>);
}

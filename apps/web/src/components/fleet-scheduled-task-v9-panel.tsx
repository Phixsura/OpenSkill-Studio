"use client";
export function FleetScheduledTaskV9Panel({ total, onTime }: { total: number; onTime: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📅 Scheduled Task v9</h3>
    <div className="text-sm">{total} tasks · {onTime} on time</div>
  </div>);
}

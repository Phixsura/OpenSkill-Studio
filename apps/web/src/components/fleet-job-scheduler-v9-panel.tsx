"use client";
export function FleetJobSchedulerV9Panel({ total, running }: { total: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Job Scheduler v9</h3>
    <div className="text-sm">{total} jobs · {running} running</div>
  </div>);
}

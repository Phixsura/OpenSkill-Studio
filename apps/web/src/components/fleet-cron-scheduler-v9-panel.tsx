"use client";
export function FleetCronSchedulerV9Panel({ jobs, running }: { jobs: number; running: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ Cron Scheduler v9</h3>
    <div className="text-sm">{jobs} jobs · {running} running</div>
  </div>);
}

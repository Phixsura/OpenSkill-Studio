"use client";
export function FleetCloudSchedPanel({ jobs, enabled, executions, failed }: { jobs: number; enabled: number; executions: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ Cloud Scheduler</h3>
    <div className="text-sm">{enabled}/{jobs} enabled · {executions} executions</div>
    {failed > 0 && <span className="text-xs text-red-500">❌ {failed} failed</span>}
  </div>);
}

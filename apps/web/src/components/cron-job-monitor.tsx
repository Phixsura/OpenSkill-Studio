"use client";

interface CronJob { name: string; successRate: number; avgDuration: number;
  consecutiveFailures: number; healthy: boolean; runs: number; }
interface CronJobMonitorProps { jobs: CronJob[]; }

export function CronJobMonitor({ jobs }: CronJobMonitorProps) {
  const unhealthy = jobs.filter(j => !j.healthy).length;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Cron Jobs</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{jobs.length} jobs</span>
          {unhealthy > 0 && <span className="text-red-500">{unhealthy} unhealthy</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {jobs.map(j => (
          <div key={j.name} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${j.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{j.name}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{j.successRate}%</span>
              <span>{j.avgDuration}s avg</span>
              <span>{j.runs} runs</span>
              {j.consecutiveFailures > 0 && <span className="text-red-500">{j.consecutiveFailures}× failed</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

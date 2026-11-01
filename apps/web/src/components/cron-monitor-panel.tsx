"use client";
interface CronJob { name: string; schedule: string; runs: number; failures: number; lastStatus: string; }
interface CronMonitorPanelProps { jobs: CronJob[]; successRate: number; totalRuns: number; }
export function CronMonitorPanel({ jobs, successRate, totalRuns }: CronMonitorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Cron Monitor</h3>
        <span className="text-xs text-gray-400">{totalRuns} runs · {successRate}% success</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {jobs.map(j => (
          <div key={j.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${j.lastStatus === "success" ? "bg-green-500" : j.lastStatus === "failed" ? "bg-red-500" : "bg-gray-400"}`} />
              <span className="font-mono">{j.name}</span>
              <span className="text-gray-400">{j.schedule}</span>
            </div>
            <span className="text-gray-400">{j.runs} runs · {j.failures} fails</span>
          </div>
        ))}
      </div>
    </div>
  );
}

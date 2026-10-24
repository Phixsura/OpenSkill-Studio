"use client";
interface Check { name: string; status: string; interval: number; consecutiveFailures: number; }
interface HcSchedulerPanelProps { checks: Check[]; healthy: number; unhealthy: number; }
export function HcSchedulerPanel({ checks, healthy, unhealthy }: HcSchedulerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Health Check Scheduler</h3>
        <span className={`text-xs ${unhealthy > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {healthy} healthy{unhealthy > 0 ? ` · ${unhealthy} unhealthy` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.name} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${c.status === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{c.name}</span>
            </div>
            <span className="text-gray-400">every {c.interval}s{c.consecutiveFailures > 0 ? ` · ${c.consecutiveFailures} fails` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

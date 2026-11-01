"use client";

interface HealthCheck { name: string; url: string; interval: string; healthy: boolean; latencyMs: number; }
interface HealthCheckSchedulerProps { checks: HealthCheck[]; allHealthy: boolean;
  onAdd: () => void; }

export function HealthCheckScheduler({ checks, allHealthy, onAdd }: HealthCheckSchedulerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold">🩺 Health Checks</h3>
          <span className={`text-xs ${allHealthy ? "text-green-600" : "text-red-500"}`}>
            {allHealthy ? "✅ All healthy" : "⚠️ Issues detected"}
          </span>
        </div>
        <button onClick={onAdd} className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">+ Add</button>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.name} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${c.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{c.name}</span>
              <span className="text-xs text-gray-400 font-mono">{c.url}</span>
            </div>
            <div className="flex gap-2 text-xs text-gray-400">
              <span>{c.latencyMs}ms</span>
              <span>every {c.interval}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

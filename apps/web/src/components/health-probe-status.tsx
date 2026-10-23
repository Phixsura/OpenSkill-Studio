"use client";

interface DepStatus { name: string; ready: boolean; latencyMs: number; }
interface HealthProbeStatusProps { ready: boolean; status: string; dependencies: DepStatus[]; }

export function HealthProbeStatus({ ready, status, dependencies }: HealthProbeStatusProps) {
  return (
    <div className={`rounded-xl border p-4 ${ready ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">{ready ? "💚" : "❤️‍🔥"}</span>
        <span className="text-sm font-semibold capitalize">{status}</span>
      </div>
      <div className="space-y-1">
        {dependencies.map(d => (
          <div key={d.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${d.ready ? "bg-green-500" : "bg-red-500"}`} />
              <span>{d.name}</span>
            </div>
            <span className="text-xs text-gray-400">{d.latencyMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}

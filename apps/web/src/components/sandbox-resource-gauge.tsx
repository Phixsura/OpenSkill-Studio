"use client";

interface ResourceInfo { usage_pct: number; label: string; current: string; limit: string; }
interface SandboxResourceGaugeProps { resources: ResourceInfo[]; status: string; uptimeSec: number; }

export function SandboxResourceGauge({ resources, status, uptimeSec }: SandboxResourceGaugeProps) {
  const hours = Math.floor(uptimeSec / 3600);
  const mins = Math.floor((uptimeSec % 3600) / 60);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Sandbox Resources</h2>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${status === "running" ? "bg-green-500" : "bg-gray-400"}`} />
          <span className="text-xs text-gray-400">{status} · {hours}h {mins}m</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {resources.map(r => {
          const color = r.usage_pct > 90 ? "bg-red-500" : r.usage_pct > 70 ? "bg-yellow-500" : "bg-green-500";
          return (
            <div key={r.label} className="rounded-lg border p-3 dark:border-gray-700">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{r.label}</span>
                <span className="text-gray-400">{r.usage_pct}%</span>
              </div>
              <div className="mt-1.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(r.usage_pct, 100)}%` }} />
              </div>
              <p className="mt-1 text-xs text-gray-400">{r.current} / {r.limit}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

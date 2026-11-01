"use client";

interface Component { name: string; type: string; status: string; latency_ms: number; error_rate: number; uptime_pct: number; }
interface HealthDashboardGridProps { components: Component[]; overall: string; }

const statusIcon: Record<string, string> = { healthy: "🟢", degraded: "🟡", down: "🔴" };

export function HealthDashboardGrid({ components, overall }: HealthDashboardGridProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">System Health</h2>
        <span className="text-sm">{statusIcon[overall] ?? "⚪"} {overall}</span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {components.map(c => (
          <div key={c.name} className={`rounded-lg border p-3 ${c.status === "down" ? "border-red-300 dark:border-red-700" : c.status === "degraded" ? "border-yellow-300 dark:border-yellow-700" : "dark:border-gray-700"}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{c.name}</span>
              <span>{statusIcon[c.status]}</span>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-1 text-center text-xs">
              <div><p className="font-bold">{c.latency_ms}ms</p><p className="text-gray-400">Latency</p></div>
              <div><p className="font-bold">{c.error_rate}%</p><p className="text-gray-400">Errors</p></div>
              <div><p className="font-bold">{c.uptime_pct}%</p><p className="text-gray-400">Uptime</p></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

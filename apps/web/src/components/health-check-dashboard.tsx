"use client";

interface HealthCheck { service: string; status: string; latencyMs: number; message: string; }
interface HealthCheckDashboardProps { checks: HealthCheck[]; overall: string; healthPct: number; }

const STATUS_ICON: Record<string, string> = { healthy: "🟢", unhealthy: "🔴", degraded: "🟡" };

export function HealthCheckDashboard({ checks, overall, healthPct }: HealthCheckDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 System Health</h3>
        <div className="flex items-center gap-2">
          <span>{STATUS_ICON[overall] ?? "⚪"}</span>
          <span className="text-xs font-medium capitalize">{overall}</span>
          <span className="text-xs text-gray-400">{healthPct}%</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.service} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{STATUS_ICON[c.status] ?? "⚪"}</span>
              <span className="text-sm font-medium">{c.service}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{c.latencyMs}ms</span>
              {c.message && <span>{c.message}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

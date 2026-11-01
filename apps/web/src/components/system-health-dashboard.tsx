"use client";

interface HealthCheck { name: string; status: string; latencyMs: number; message: string; }
interface SystemHealthDashboardProps { overall: string; healthDisplay: string;
  healthy: number; total: number; checks: HealthCheck[]; }

export function SystemHealthDashboard({ overall, healthDisplay, healthy, total, checks }: SystemHealthDashboardProps) {
  const emoji = overall === "healthy" ? "🟢" : overall === "degraded" ? "🟡" : "🔴";
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🏥 System Health</h3>
        <div className="flex items-center gap-2">
          <span className="text-lg">{emoji}</span>
          <span className="text-sm font-bold capitalize">{overall}</span>
          <span className="text-xs text-gray-400">{healthDisplay}</span>
        </div>
      </div>
      <div className="space-y-2">
        {checks.map(c => (
          <div key={c.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${c.status === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{c.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              {c.message && <span className="text-red-500">{c.message}</span>}
              <span>{c.latencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 text-xs text-gray-400 text-center">{healthy}/{total} services healthy</div>
    </div>
  );
}

"use client";

interface AppHealth { name: string; icon: string; status: string; uptimePct: number;
  responseMs: number; errorRatePct: number; }
interface HealthMonitorDashboardProps { apps: AppHealth[]; overall: string;
  healthy: number; degraded: number; down: number; }

const statusColors: Record<string, string> = {
  healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500",
};
const overallLabels: Record<string, string> = {
  healthy: "🟢 All Systems Operational", degraded: "🟡 Partial Degradation", outage: "🔴 Service Outage",
};

export function HealthMonitorDashboard({ apps, overall, healthy, degraded, down }: HealthMonitorDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border p-4 dark:border-gray-700">
        <p className="text-lg font-bold">{overallLabels[overall] ?? overall}</p>
        <div className="mt-2 flex gap-4 text-xs">
          <span className="text-green-600">{healthy} healthy</span>
          {degraded > 0 && <span className="text-yellow-600">{degraded} degraded</span>}
          {down > 0 && <span className="text-red-600">{down} down</span>}
        </div>
      </div>
      <div className="space-y-2">
        {apps.map(a => (
          <div key={a.name} className="flex items-center justify-between rounded-lg border px-4 py-2.5 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${statusColors[a.status] ?? ""}`} />
              <span className="text-sm">{a.icon}</span>
              <span className="text-sm font-medium">{a.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{a.uptimePct}%</span>
              <span>{a.responseMs}ms</span>
              {a.errorRatePct > 0 && <span className="text-red-500">{a.errorRatePct}% err</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

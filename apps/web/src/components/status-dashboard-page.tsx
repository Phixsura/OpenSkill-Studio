"use client";

interface Service { name: string; status: string; }
interface StatusDashboardPageProps { overallStatus: string; uptimePct: number; services: Service[]; activeIncidents: number; }

const STATUS_LABELS: Record<string, { label: string; color: string; icon: string }> = {
  operational: { label: "All Systems Operational", color: "text-green-600 bg-green-50", icon: "✅" },
  partial_outage: { label: "Partial System Outage", color: "text-yellow-600 bg-yellow-50", icon: "⚠️" },
  major_outage: { label: "Major System Outage", color: "text-red-600 bg-red-50", icon: "🔴" },
};

const SVC_COLORS: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", major_outage: "bg-red-500" };

export function StatusDashboardPage({ overallStatus, uptimePct, services, activeIncidents }: StatusDashboardPageProps) {
  const overall = STATUS_LABELS[overallStatus] || STATUS_LABELS.operational;
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className={`rounded-xl p-6 text-center ${overall.color}`}>
        <span className="text-3xl">{overall.icon}</span>
        <h1 className="mt-2 text-xl font-bold">{overall.label}</h1>
        <p className="mt-1 text-sm opacity-70">Uptime: {uptimePct}% (90 days)</p>
        {activeIncidents > 0 && <p className="mt-1 text-sm font-medium">{activeIncidents} active incident{activeIncidents > 1 ? "s" : ""}</p>}
      </div>
      <div className="space-y-2">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between rounded-lg border border-gray-200 p-3 dark:border-gray-700">
            <span className="text-sm font-medium">{s.name}</span>
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${SVC_COLORS[s.status] || "bg-gray-300"}`} />
              <span className="text-xs text-gray-400 capitalize">{s.status.replace("_", " ")}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

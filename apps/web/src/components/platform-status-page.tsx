"use client";

interface Service { name: string; status: string; }
interface PlatformStatusPageProps { overallStatus: string; services: Service[];
  uptime90d: number; activeIncidents: number; lastIncidentDaysAgo: number; updatedAt: string; }

const statusConfig: Record<string, { label: string; color: string; icon: string; bg: string }> = {
  all_operational: { label: "All Systems Operational", color: "text-green-600", icon: "🟢", bg: "bg-green-50 dark:bg-green-900/10" },
  partial_outage: { label: "Partial System Outage", color: "text-yellow-600", icon: "🟡", bg: "bg-yellow-50 dark:bg-yellow-900/10" },
  major_outage: { label: "Major Outage", color: "text-red-600", icon: "🔴", bg: "bg-red-50 dark:bg-red-900/10" },
  investigating: { label: "Investigating Issue", color: "text-blue-600", icon: "🔵", bg: "bg-blue-50 dark:bg-blue-900/10" },
};
const svcIcon: Record<string, string> = { operational: "🟢", degraded: "🟡", outage: "🔴" };

export function PlatformStatusPage({ overallStatus, services, uptime90d, activeIncidents, lastIncidentDaysAgo, updatedAt }: PlatformStatusPageProps) {
  const cfg = statusConfig[overallStatus] ?? statusConfig.all_operational;
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className={`rounded-xl p-6 text-center ${cfg.bg}`}>
        <span className="text-3xl">{cfg.icon}</span>
        <h1 className={`mt-2 text-2xl font-black ${cfg.color}`}>{cfg.label}</h1>
        <p className="mt-1 text-xs text-gray-400">Last updated: {new Date(updatedAt).toLocaleString()}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg border p-3 dark:border-gray-700">
          <p className="text-xl font-bold">{uptime90d}%</p><p className="text-xs text-gray-400">90-day Uptime</p>
        </div>
        <div className="rounded-lg border p-3 dark:border-gray-700">
          <p className="text-xl font-bold">{activeIncidents}</p><p className="text-xs text-gray-400">Active Incidents</p>
        </div>
        <div className="rounded-lg border p-3 dark:border-gray-700">
          <p className="text-xl font-bold">{lastIncidentDaysAgo}d</p><p className="text-xs text-gray-400">Since Last Incident</p>
        </div>
      </div>
      <div className="space-y-2">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between rounded-lg border px-4 py-3 dark:border-gray-700">
            <span className="font-medium">{s.name}</span>
            <span>{svcIcon[s.status] ?? "⚪"} <span className="text-sm capitalize text-gray-500">{s.status}</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}

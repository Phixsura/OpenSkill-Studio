"use client";

interface ServiceStatus { name: string; status: string; icon: string; uptime_pct: number; response_ms: number | null; }
interface Incident { title: string; status: string; timestamp: string; }
interface StatusPageProps { services: ServiceStatus[]; overall: string; overallIcon: string; incidents: Incident[]; }

export function StatusPage({ services, overall, overallIcon, incidents }: StatusPageProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 rounded-xl border p-4 dark:border-gray-700">
        <span className="text-2xl">{overallIcon}</span>
        <div>
          <p className="text-lg font-bold capitalize">{overall === "operational" ? "All Systems Operational" : `Systems ${overall}`}</p>
        </div>
      </div>
      <div className="space-y-2">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between rounded-lg border px-4 py-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{s.icon}</span>
              <span className="text-sm font-medium">{s.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              {s.response_ms != null && <span>{s.response_ms}ms</span>}
              <span>{s.uptime_pct}%</span>
            </div>
          </div>
        ))}
      </div>
      {incidents.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Active Incidents</h3>
          {incidents.map((inc, i) => (
            <div key={i} className="rounded-lg border-l-4 border-yellow-500 bg-yellow-50 p-3 dark:bg-yellow-900/10">
              <p className="text-sm font-medium">{inc.title}</p>
              <p className="text-xs text-gray-500 capitalize">{inc.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

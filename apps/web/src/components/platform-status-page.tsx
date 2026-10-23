"use client";

interface Service { id: string; name: string; status: string; icon: string; }
interface Incident { title: string; status: string; updated: string; }
interface PlatformStatusPageProps { groups: Record<string, Service[]>; overall: string;
  overallLabel: string; healthy: number; incidents: Incident[]; updatedAt: string; }

export function PlatformStatusPage({ groups, overall, overallLabel, healthy, incidents, updatedAt }: PlatformStatusPageProps) {
  const overallIcon = overall === "operational" ? "🟢" : overall === "degraded" ? "🟡" : "🔴";
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-xl border p-6 text-center dark:border-gray-700">
        <span className="text-4xl">{overallIcon}</span>
        <h1 className="mt-2 text-xl font-bold">{overallLabel}</h1>
        <p className="text-xs text-gray-400 mt-1">Updated {new Date(updatedAt).toLocaleString()}</p>
      </div>
      {Object.entries(groups).map(([group, services]) => (
        <div key={group}>
          <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">{group}</h3>
          <div className="space-y-1">
            {services.map(s => (
              <div key={s.id} className="flex items-center justify-between rounded-lg border px-4 py-2 dark:border-gray-700">
                <span className="text-sm">{s.name}</span>
                <div className="flex items-center gap-1.5">
                  <span>{s.icon}</span>
                  <span className="text-xs text-gray-400 capitalize">{s.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
      {incidents.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-2">⚠ Active Incidents</h3>
          {incidents.map((inc, i) => (
            <div key={i} className="rounded-lg border-l-4 border-yellow-500 bg-yellow-50 p-3 dark:bg-yellow-900/10">
              <p className="text-sm font-medium">{inc.title}</p>
              <p className="text-xs text-gray-400 capitalize">{inc.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

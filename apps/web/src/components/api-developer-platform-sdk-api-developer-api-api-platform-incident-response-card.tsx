"use client";

interface IncidentInfo { incident_id: string; title: string; severity: string; status: string; commander: string; duration_minutes: number; affected_services: string[]; }
interface Props { incidents: IncidentInfo[]; activeCount: number; mttrMinutes: number; appName: string; }

const sevColor: Record<string, string> = { sev1: "bg-red-100 text-red-700", sev2: "bg-orange-100 text-orange-700", sev3: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponseCard({ incidents, activeCount, mttrMinutes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Incident Response</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · MTTR: {mttrMinutes}m</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{activeCount} active</span>}
      </div>
      {incidents.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No incidents</p>
      ) : (
        <div className="space-y-2">
          {incidents.slice(0, 5).map((i) => (
            <div key={i.incident_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${sevColor[i.severity] ?? ""}`}>{i.severity}</span>
                  <span className="text-gray-700 dark:text-gray-300">{i.title}</span>
                </div>
                <span className="text-gray-400">{i.status} · {i.duration_minutes}m</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">IC: {i.commander} · {i.affected_services.length} services</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

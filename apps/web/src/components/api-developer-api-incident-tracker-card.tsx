"use client";

interface IncidentInfo { incident_id: string; title: string; severity: string; status: string; duration_minutes: number; affected_endpoints: string[]; }
interface Props { incidents: IncidentInfo[]; mttrMinutes: number; appName: string; }

const sevColor: Record<string, string> = { critical: "bg-red-100 text-red-700", major: "bg-orange-100 text-orange-700", minor: "bg-yellow-100 text-yellow-700" };
const statDot: Record<string, string> = { open: "bg-red-500", investigating: "bg-yellow-500", resolved: "bg-green-500" };

export default function APIDeveloperAPIIncidentTrackerCard({ incidents, mttrMinutes, appName }: Props) {
  const openCount = incidents.filter(i => i.status !== "resolved").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Incident Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          {openCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{openCount} open</span>}
          <p className="text-[9px] text-gray-400 mt-0.5">MTTR: {mttrMinutes}m</p>
        </div>
      </div>
      {incidents.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No incidents</p>
      ) : (
        <div className="space-y-2">
          {incidents.map((i) => (
            <div key={i.incident_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center gap-1.5 text-[11px]">
                <span className={`h-1.5 w-1.5 rounded-full ${statDot[i.status] ?? "bg-gray-400"}`} />
                <span className="font-medium text-gray-700 dark:text-gray-300">{i.title}</span>
                <span className={`ml-auto rounded-full px-1.5 py-0.5 text-[9px] ${sevColor[i.severity] ?? ""}`}>{i.severity}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{i.duration_minutes}m · {i.affected_endpoints.length} endpoints</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

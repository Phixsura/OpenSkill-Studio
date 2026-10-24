"use client";

interface Incident { id: string; title: string; severity: string; severityLabel: string; status: string; }
interface IncidentTrackerProps { incidents: Incident[]; active: number; hasCritical: boolean; }

const sevColors: Record<string, string> = {
  sev1: "bg-red-500", sev2: "bg-orange-500", sev3: "bg-yellow-500", sev4: "bg-blue-500",
};
const statusBadge: Record<string, string> = {
  investigating: "bg-red-100 text-red-700 dark:bg-red-900/30",
  identified: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  monitoring: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  resolved: "bg-green-100 text-green-700 dark:bg-green-900/30",
};

export function IncidentTracker({ incidents, active, hasCritical }: IncidentTrackerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Incidents</h3>
        <div className="flex items-center gap-2">
          {hasCritical && <span className="animate-pulse text-xs text-red-600">🚨 Critical</span>}
          <span className="text-xs text-gray-400">{active} active</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {incidents.map(i => (
          <div key={i.id} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${sevColors[i.severity] ?? "bg-gray-400"}`} />
              <div>
                <p className="text-sm font-medium">{i.title}</p>
                <p className="text-xs text-gray-400">{i.id} · {i.severityLabel}</p>
              </div>
            </div>
            <span className={`rounded px-2 py-0.5 text-xs ${statusBadge[i.status] ?? ""}`}>{i.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

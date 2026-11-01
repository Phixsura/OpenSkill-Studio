"use client";

interface IncidentInfo {
  incident_id: string;
  title: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "investigating" | "mitigated" | "resolved";
  affected_endpoints: string[];
}

interface APIIncidentTrackerCardProps {
  incidents: IncidentInfo[];
  appName: string;
}

const sevStyle: Record<string, string> = {
  low: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APIIncidentTrackerCard({ incidents, appName }: APIIncidentTrackerCardProps) {
  const active = incidents.filter((i) => i.status !== "resolved").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Incident Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{incidents.length} incidents</span>
          {active > 0 && <p className="text-[10px] text-red-500">{active} active</p>}
        </div>
      </div>

      {incidents.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">No incidents</p>
      ) : (
        <div className="space-y-1.5">
          {incidents.map((i) => (
            <div key={i.incident_id} className={`rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${i.status === "resolved" ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${sevStyle[i.severity]}`}>{i.severity}</span>
                  <span className="text-xs text-gray-700 dark:text-gray-300">{i.title}</span>
                </div>
                <span className="text-[10px] text-gray-400">{i.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

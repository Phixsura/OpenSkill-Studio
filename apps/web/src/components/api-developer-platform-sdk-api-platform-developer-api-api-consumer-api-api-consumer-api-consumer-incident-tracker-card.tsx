"use client";

interface Incident { id: string; title: string; severity: string; status: string; affectedEndpoints: string[]; createdAt: string; }
interface Props { incidents: Incident[]; appName: string; }

const severityColors: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  major: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  minor: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTrackerCard({ incidents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Incidents</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {incidents.length} active</p>
      </div>
      {incidents.length === 0 ? (
        <p className="text-center text-sm text-green-500">All systems operational</p>
      ) : (
        <div className="space-y-2">
          {incidents.map((i) => (
            <div key={i.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{i.title}</span>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${severityColors[i.severity] ?? ""}`}>{i.severity}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{i.status} · {i.createdAt}{i.affectedEndpoints.length > 0 && ` · ${i.affectedEndpoints.join(", ")}`}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

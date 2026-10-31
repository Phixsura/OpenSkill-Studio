"use client";

interface ComponentInfo { component_id: string; name: string; status: string; }
interface IncidentInfo { incident_id: string; title: string; status: string; impact: string; }
interface Props { components: ComponentInfo[]; incidents: IncidentInfo[]; overallStatus: string; appName: string; }

const statusStyle: Record<string, string> = { operational: "text-green-600 dark:text-green-400", degraded: "text-yellow-600 dark:text-yellow-400", partial_outage: "text-orange-600 dark:text-orange-400", major_outage: "text-red-600 dark:text-red-400", maintenance: "text-blue-600 dark:text-blue-400" };
const statusDot: Record<string, string> = { operational: "🟢", degraded: "🟡", partial_outage: "🟠", major_outage: "🔴", maintenance: "🔵" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPageCard({ components, incidents, overallStatus, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Status Page</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${statusStyle[overallStatus] ?? ""}`}>{statusDot[overallStatus] ?? "⚪"} {overallStatus.replace("_", " ")}</span>
      </div>
      <div className="mb-3 space-y-1">
        {components.map((c) => (
          <div key={c.component_id} className="flex items-center justify-between text-[11px]">
            <span className="text-gray-700 dark:text-gray-300">{c.name}</span>
            <span className={statusStyle[c.status] ?? ""}>{statusDot[c.status] ?? "⚪"}</span>
          </div>
        ))}
      </div>
      {incidents.length > 0 && (
        <div className="border-t border-gray-100 pt-2 dark:border-gray-800">
          <p className="mb-1 text-[10px] font-medium text-gray-500">Active Incidents</p>
          {incidents.map((i) => (
            <div key={i.incident_id} className="text-[11px] text-gray-700 dark:text-gray-300">⚠️ {i.title} ({i.status})</div>
          ))}
        </div>
      )}
    </div>
  );
}

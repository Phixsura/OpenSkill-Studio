"use client";

interface Component { id: string; name: string; status: string; }
interface Props { overallStatus: string; components: Component[]; activeIncidents: number; uptime30d: number; appName: string; }

const statusColors: Record<string, string> = {
  operational: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  degraded: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  partial_outage: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  major_outage: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};
const statusDot: Record<string, string> = {
  operational: "bg-green-500", degraded: "bg-amber-500", partial_outage: "bg-orange-500", major_outage: "bg-red-500",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPageCard({ overallStatus, components, activeIncidents, uptime30d, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Status Page</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {uptime30d}% uptime (30d)</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${statusColors[overallStatus] ?? ""}`}>{overallStatus.replace("_", " ")}</span>
      </div>
      {activeIncidents > 0 && <div className="mb-2 rounded bg-red-50 p-1.5 text-center text-[11px] text-red-600 dark:bg-red-900/20">{activeIncidents} active incident{activeIncidents > 1 ? "s" : ""}</div>}
      {components.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No components</p>
      ) : (
        <div className="space-y-1">
          {components.map((c) => (
            <div key={c.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <span className="text-gray-700 dark:text-gray-300">{c.name}</span>
              <div className="flex items-center gap-1">
                <span className={`h-2 w-2 rounded-full ${statusDot[c.status] ?? ""}`} />
                <span className="text-[10px] text-gray-400">{c.status.replace("_", " ")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

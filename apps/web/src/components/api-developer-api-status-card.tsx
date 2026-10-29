"use client";

interface StatusInfo { service_name: string; status: string; response_time_ms: number; }
interface Props { statuses: StatusInfo[]; overallStatus: string; appName: string; }

const sDot: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", outage: "bg-red-500" };
const sBanner: Record<string, string> = { operational: "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300", degraded: "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300", outage: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300" };

export default function APIDeveloperAPIStatusCard({ statuses, overallStatus, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🟢 API Status</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${sBanner[overallStatus] ?? ""}`}>{overallStatus}</span>
      </div>
      {statuses.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No status data</p>
      ) : (
        <div className="space-y-1">
          {statuses.map((s) => (
            <div key={s.service_name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[s.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{s.service_name}</span>
              </div>
              <span className="text-gray-400">{s.response_time_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

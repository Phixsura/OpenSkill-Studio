"use client";

interface ProbeInfo { probe_id: string; endpoint: string; current_status: string; consecutive_healthy: number; consecutive_unhealthy: number; }
interface Props { probes: ProbeInfo[]; unhealthyCount: number; appName: string; }

const statusStyle: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", degraded: "text-yellow-600 dark:text-yellow-400", unhealthy: "text-red-600 dark:text-red-400", unknown: "text-gray-400" };
const statusDot: Record<string, string> = { healthy: "🟢", degraded: "🟡", unhealthy: "🔴", unknown: "⚪" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbeCard({ probes, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💓 Health Probes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {probes.length} probes</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {unhealthyCount} down</span>}
      </div>
      {probes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health probes</p>
      ) : (
        <div className="space-y-1">
          {probes.map((p) => (
            <div key={p.probe_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{statusDot[p.current_status] ?? "⚪"}</span>
                <span className="text-gray-700 dark:text-gray-300">{p.endpoint}</span>
              </div>
              <span className={statusStyle[p.current_status] ?? "text-gray-400"}>{p.current_status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

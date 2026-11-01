"use client";

interface SlaInfo { endpoint: string; method: string; meeting_sla: boolean; actual_uptime: number; target_uptime: number; actual_p99: number; target_p99: number; violations: string[]; }
interface Props { slas: SlaInfo[]; violationCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSlaCard({ slas, violationCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Endpoint SLAs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {slas.length} SLAs</p>
        </div>
        {violationCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {violationCount} violations</span>}
      </div>
      {slas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLAs defined</p>
      ) : (
        <div className="space-y-1">
          {slas.map((s) => (
            <div key={`${s.method}-${s.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.meeting_sla ? "✅" : "❌"} {s.method} {s.endpoint}</span>
              <span className="text-gray-400">{s.actual_uptime}% / {s.actual_p99}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

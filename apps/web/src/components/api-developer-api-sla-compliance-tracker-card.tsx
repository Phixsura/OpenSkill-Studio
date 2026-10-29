"use client";

interface SLAInfo { endpoint: string; uptime_target_pct: number; actual_uptime_pct: number; latency_p99_target_ms: number; actual_latency_p99_ms: number; compliant: boolean; violation_rate_pct: number; }
interface Props { targets: SLAInfo[]; nonCompliantCount: number; appName: string; }

export default function APIDeveloperAPISLAComplianceTrackerCard({ targets, nonCompliantCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 SLA Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {nonCompliantCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{nonCompliantCount} breached</span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">all compliant</span>
        )}
      </div>
      {targets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLA targets</p>
      ) : (
        <div className="space-y-2">
          {targets.map((t) => (
            <div key={t.endpoint} className={`rounded-lg p-2 ${t.compliant ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.endpoint}</span>
                <span className={t.compliant ? "text-green-600" : "text-red-500 font-bold"}>{t.compliant ? "✓" : "✗"}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>uptime: {t.actual_uptime_pct}% / {t.uptime_target_pct}%</span>
                <span>p99: {t.actual_latency_p99_ms}ms / {t.latency_p99_target_ms}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

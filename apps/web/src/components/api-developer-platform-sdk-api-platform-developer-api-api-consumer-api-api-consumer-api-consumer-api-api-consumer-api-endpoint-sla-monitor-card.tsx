"use client";

interface Report { path: string; inCompliance: boolean; availability: number; latencyP99: number; errorRate: number; availOk: boolean; latOk: boolean; errOk: boolean; }
interface Props { reports: Report[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitorCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 SLA Monitor</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {reports.length} endpoints</p>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLA targets</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.path} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{r.path}</code>
                <span className={`font-bold ${r.inCompliance ? "text-green-600" : "text-red-600"}`}>{r.inCompliance ? "✅" : "❌"}</span>
              </div>
              <div className="mt-0.5 grid grid-cols-3 gap-1 text-center text-[10px]">
                <span className={r.availOk ? "text-green-500" : "text-red-500"}>{r.availability}% avail</span>
                <span className={r.latOk ? "text-green-500" : "text-red-500"}>{r.latencyP99}ms p99</span>
                <span className={r.errOk ? "text-green-500" : "text-red-500"}>{r.errorRate}% err</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

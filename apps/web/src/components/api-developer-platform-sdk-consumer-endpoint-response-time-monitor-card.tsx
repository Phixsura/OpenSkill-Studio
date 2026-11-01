"use client";

interface Report { path: string; sampleCount: number; p50: number; p95: number; p99: number; p50Ok: boolean; p95Ok: boolean; p99Ok: boolean; allOk: boolean; }
interface Props { reports: Report[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerEndpointResponseTimeMonitorCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Response Time Monitor</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {reports.length} endpoints</p>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No response time data</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.path} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{r.path}</code>
                <span className={r.allOk ? "text-green-500" : "text-red-500"}>{r.allOk ? "✅" : "⚠️"}</span>
              </div>
              <div className="mt-0.5 grid grid-cols-3 gap-1 text-center text-[10px]">
                <span className={r.p50Ok ? "text-green-500" : "text-red-500"}>P50: {r.p50}ms</span>
                <span className={r.p95Ok ? "text-green-500" : "text-red-500"}>P95: {r.p95}ms</span>
                <span className={r.p99Ok ? "text-green-500" : "text-red-500"}>P99: {r.p99}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

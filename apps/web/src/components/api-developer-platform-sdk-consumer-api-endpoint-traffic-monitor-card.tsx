"use client";

interface Alert { type: string; message: string; }
interface Summary { endpoint: string; currentRps: number; peakRps: number; avgRps: number; totalRequests: number; alerts: Alert[]; }
interface Props { summaries: Summary[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiEndpointTrafficMonitorCard({ summaries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Traffic Monitor</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {summaries.length} endpoints</p>
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traffic data</p>
      ) : (
        <div className="space-y-2">
          {summaries.map((s) => (
            <div key={s.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{s.endpoint}</code>
                <span className="font-bold text-blue-600">{s.currentRps} rps</span>
              </div>
              <div className="mt-0.5 grid grid-cols-3 gap-1 text-center text-[10px] text-gray-400">
                <span>Peak: {s.peakRps}</span>
                <span>Avg: {s.avgRps}</span>
                <span>{s.totalRequests.toLocaleString()} total</span>
              </div>
              {s.alerts.length > 0 && <div className="mt-1 text-[9px] text-red-500">{s.alerts.map(a => a.message).join(" · ")}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

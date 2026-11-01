"use client";

interface RateInfo { endpoint: string; error_rate_pct: number; total_requests: number; status: string; last_error_code: string; }
interface Props { endpoints: RateInfo[]; overallRate: number; criticalCount: number; appName: string; }

const sColor: Record<string, string> = { normal: "text-green-600", elevated: "text-yellow-600", warning: "text-orange-600", critical: "text-red-600" };

export default function APIDeveloperPlatformSDKApiEndpointErrorRateMonitorCard({ endpoints, overallRate, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📉 Error Rates</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · overall: {overallRate}%</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{criticalCount} critical</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.slice(0, 5).map((e) => (
            <div key={e.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.endpoint}</span>
              <span className={`font-bold ${sColor[e.status] ?? ""}`}>{e.error_rate_pct}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

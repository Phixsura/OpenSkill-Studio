"use client";

interface Metric { path: string; requests: number; avgMs: number; errorRate: number; }
interface Props { totalRequests: number; totalErrors: number; overallAvgMs: number; overallErrorRate: number; topEndpoints: Metric[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregatorCard({ totalRequests, totalErrors, overallAvgMs, overallErrorRate, topEndpoints, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Endpoint Metrics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="mb-3 grid grid-cols-4 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalRequests.toLocaleString()}</div><div className="text-[9px] text-gray-400">Requests</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-red-600">{totalErrors}</div><div className="text-[9px] text-gray-400">Errors</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{overallAvgMs}ms</div><div className="text-[9px] text-gray-400">Avg</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${overallErrorRate > 1 ? "text-red-600" : "text-green-600"}`}>{overallErrorRate}%</div><div className="text-[9px] text-gray-400">Err%</div></div>
      </div>
      {topEndpoints.length > 0 && (
        <div className="space-y-0.5">
          {topEndpoints.map((e) => (
            <div key={e.path} className="flex items-center justify-between text-[10px]">
              <code className="text-gray-600 dark:text-gray-400">{e.path}</code>
              <span className="text-gray-400">{e.requests} req · {e.avgMs}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

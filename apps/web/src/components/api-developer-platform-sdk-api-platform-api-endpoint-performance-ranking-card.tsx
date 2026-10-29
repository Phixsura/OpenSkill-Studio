"use client";

interface PerfInfo { endpoint: string; performance_score: number; rank_label: string; avg_latency_ms: number; p99_latency_ms: number; error_rate_pct: number; }
interface Props { endpoints: PerfInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRankingCard({ endpoints, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 Performance Ranking</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints</p>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No performance data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.map((e, i) => (
            <div key={e.endpoint} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="text-gray-400 font-mono w-4">#{i + 1}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.endpoint}</span>
              </div>
              <div className="flex gap-2 text-[10px]">
                <span className="text-gray-400">{e.avg_latency_ms}ms · p99:{e.p99_latency_ms}ms</span>
                <span>{e.rank_label}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

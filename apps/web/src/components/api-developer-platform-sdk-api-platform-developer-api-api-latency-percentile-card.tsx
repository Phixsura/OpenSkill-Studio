"use client";

interface LatencyInfo { endpoint: string; method: string; p50: number; p95: number; p99: number; avg: number; count: number; }
interface Props { endpoints: LatencyInfo[]; slowCount: number; appName: string; }

const fmtMs = (ms: number) => ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${Math.round(ms)}ms`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentileCard({ endpoints, slowCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Latency Percentiles</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints</p>
        </div>
        {slowCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🐌 {slowCount} slow</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No latency data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{e.method} {e.endpoint}</span>
                <span className="text-gray-400">{e.count.toLocaleString()} reqs</span>
              </div>
              <div className="flex gap-3 text-[10px] text-gray-400">
                <span>p50: {fmtMs(e.p50)}</span>
                <span>p95: {fmtMs(e.p95)}</span>
                <span className={e.p99 > 1000 ? "text-red-500" : ""}>p99: {fmtMs(e.p99)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

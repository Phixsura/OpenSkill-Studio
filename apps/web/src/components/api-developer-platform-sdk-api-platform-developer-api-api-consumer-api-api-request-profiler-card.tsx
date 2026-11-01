"use client";

interface ProfileInfo { endpoint: string; method: string; avg_ms: number; min_ms: number; max_ms: number; samples: number; error_pct: number; }
interface Props { profiles: ProfileInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfilerCard({ profiles, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Request Profiler</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {profiles.length} endpoints</p>
      </div>
      {profiles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No profiling data</p>
      ) : (
        <div className="space-y-1.5">
          {profiles.map((p) => (
            <div key={`${p.method}-${p.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{p.method} {p.endpoint}</span>
                <span className="text-gray-400">{p.samples.toLocaleString()} reqs</span>
              </div>
              <div className="flex gap-2 text-[10px] text-gray-400">
                <span>avg: {p.avg_ms}ms</span>
                <span>min: {p.min_ms}ms</span>
                <span>max: {p.max_ms}ms</span>
                {p.error_pct > 0 && <span className="text-red-500">{p.error_pct}% err</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

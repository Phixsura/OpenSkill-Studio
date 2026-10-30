"use client";

interface Result { benchmarkId: string; endpoint: string; rps: number; avgMs: number; p95Ms: number; p99Ms: number; successful: number; failed: number; runAt: string; }
interface Props { results: Result[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmarkCard({ results, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏎️ API Benchmarks</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No benchmarks run</p>
      ) : (
        <div className="space-y-2">
          {results.slice(0, 5).map((r, i) => (
            <div key={i} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{r.endpoint}</code>
                <span className="font-bold text-blue-600">{r.rps} rps</span>
              </div>
              <div className="mt-0.5 grid grid-cols-4 gap-1 text-center text-[10px] text-gray-400">
                <span>Avg: {r.avgMs}ms</span>
                <span>P95: {r.p95Ms}ms</span>
                <span>P99: {r.p99Ms}ms</span>
                <span className={r.failed > 0 ? "text-red-400" : "text-green-400"}>{r.successful}✓ {r.failed}✗</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

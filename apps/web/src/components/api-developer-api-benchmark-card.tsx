"use client";

interface BenchmarkInfo { benchmark_id: string; endpoint: string; rps: number; avg_latency_ms: number; p99_latency_ms: number; error_rate: number; }
interface Props { results: BenchmarkInfo[]; appName: string; }

export default function APIDeveloperAPIBenchmarkCard({ results, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏎️ API Benchmarks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{results.length} benchmarks</span>
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No benchmarks</p>
      ) : (
        <div className="space-y-1">
          {results.map((r) => (
            <div key={r.benchmark_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              <span className="text-gray-400">{r.rps.toLocaleString()} rps · {r.avg_latency_ms}ms avg · p99 {r.p99_latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

interface ResultInfo { test_id: string; endpoint: string; concurrency: number; rps: number; success_rate: number; avg_latency_ms: number; p99_latency_ms: number; passed: boolean; }
interface Props { results: ResultInfo[]; failingCount: number; appName: string; }

export default function APIDeveloperAPIApiLoadTestRunnerCard({ results, failingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏋️ Load Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {failingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{failingCount} failing</span>}
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No load tests</p>
      ) : (
        <div className="space-y-2">
          {results.map((r) => (
            <div key={r.test_id} className={`rounded-lg p-2 ${r.passed ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.endpoint}</span>
                <span className={r.passed ? "text-green-600 font-bold" : "text-red-500 font-bold"}>{r.passed ? "PASS" : "FAIL"}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>{r.rps} rps</span>
                <span>{r.success_rate}%</span>
                <span>p99: {r.p99_latency_ms}ms</span>
                <span>×{r.concurrency}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

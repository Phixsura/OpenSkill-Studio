"use client";

interface LoadTestResults { total_requests: number; successful: number; failed: number;
  actual_rps: number; p50_ms: number; p95_ms: number; p99_ms: number; error_rate: number; }
interface LoadTestResultsViewProps { testId: string; endpoint: string; concurrentUsers: number;
  results: LoadTestResults; verdict: string; onRerun: () => void; }

const verdictStyle: Record<string, string> = {
  pass: "bg-green-100 text-green-700 dark:bg-green-900/30", warning: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  fail: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function LoadTestResultsView({ testId, endpoint, concurrentUsers, results, verdict, onRerun }: LoadTestResultsViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Load Test Results</h2>
          <p className="text-xs text-gray-400">{endpoint} · {concurrentUsers} users</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-bold uppercase ${verdictStyle[verdict] ?? ""}`}>{verdict}</span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Total", value: results.total_requests.toLocaleString() },
          { label: "RPS", value: results.actual_rps.toString() },
          { label: "Error Rate", value: `${results.error_rate}%` },
          { label: "P95", value: `${results.p95_ms}ms` },
        ].map(m => (
          <div key={m.label} className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
            <p className="font-bold">{m.value}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
      <button onClick={onRerun} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Re-run Test</button>
    </div>
  );
}

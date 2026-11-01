"use client";

interface LoadTestPanelProps { rps: number; totalRequests: number; errorRatePct: number;
  p50Ms: number; p95Ms: number; p99Ms: number; passed: boolean; }

export function LoadTestPanel({ rps, totalRequests, errorRatePct, p50Ms, p95Ms, p99Ms, passed }: LoadTestPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏋️ Load Test</h3>
        <span className={`text-xs font-bold ${passed ? "text-green-600" : "text-red-500"}`}>
          {passed ? "✅ PASSED" : "❌ FAILED"} · {rps} rps
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">P50</div><div className="font-bold text-lg">{p50Ms}ms</div></div>
        <div><div className="text-gray-400">P95</div><div className="font-bold text-lg">{p95Ms}ms</div></div>
        <div><div className="text-gray-400">P99</div><div className="font-bold text-lg">{p99Ms}ms</div></div>
      </div>
      <div className="border-t dark:border-gray-700 p-3 text-center text-xs text-gray-400">
        {totalRequests.toLocaleString()} requests · {errorRatePct}% errors
      </div>
    </div>
  );
}

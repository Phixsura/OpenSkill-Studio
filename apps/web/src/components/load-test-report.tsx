"use client";

interface LoadTestReportProps { endpoint: string; rps: number; durationSec: number;
  totalRequests: number; successful: number; failed: number; avgLatencyMs: number;
  errorRatePct: number; passed: boolean; regression: boolean | null; }

export function LoadTestReport({ endpoint, rps, durationSec, totalRequests, successful, failed, avgLatencyMs, errorRatePct, passed, regression }: LoadTestReportProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">⚡ Load Test</h3>
          <div className="text-[10px] text-gray-400 font-mono">{endpoint} · {rps} RPS × {durationSec}s</div>
        </div>
        <div className="flex gap-2">
          <span className={`text-xs font-medium ${passed ? "text-green-600" : "text-red-500"}`}>
            {passed ? "✅ Passed" : "❌ Failed"}
          </span>
          {regression !== null && (
            <span className={`text-xs ${regression ? "text-red-500" : "text-green-600"}`}>
              {regression ? "📉 Regression" : "📈 Improved"}
            </span>
          )}
        </div>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Total", v: totalRequests.toLocaleString() },
          { l: "Success", v: successful.toLocaleString() },
          { l: "Latency", v: `${avgLatencyMs}ms` },
          { l: "Errors", v: `${errorRatePct}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

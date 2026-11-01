"use client";

interface LatencyBudgetInfo {
  endpoint: string;
  p50: number;
  p50_target_ms: number;
  p95: number;
  p95_target_ms: number;
  p99: number;
  p99_target_ms: number;
  violations: string[];
}

interface APILatencyBudgetCardProps {
  budgets: LatencyBudgetInfo[];
  appName: string;
}

export default function APILatencyBudgetCard({ budgets, appName }: APILatencyBudgetCardProps) {
  const violating = budgets.filter((b) => b.violations.length > 0).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⏱️ Latency Budgets
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{budgets.length} endpoints</span>
          {violating > 0 && <p className="text-[10px] text-red-500">{violating} violating</p>}
        </div>
      </div>

      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No latency budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div
              key={b.endpoint}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {b.endpoint}
                </span>
                {b.violations.length > 0 && (
                  <span className="text-[10px] text-red-500">{b.violations.join(", ")}</span>
                )}
              </div>
              <div className="mt-1 flex gap-3 text-[10px] text-gray-400">
                <span className={b.violations.includes("p50") ? "text-red-500" : ""}>
                  p50: {b.p50}ms
                </span>
                <span className={b.violations.includes("p95") ? "text-red-500" : ""}>
                  p95: {b.p95}ms
                </span>
                <span className={b.violations.includes("p99") ? "text-red-500" : ""}>
                  p99: {b.p99}ms
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

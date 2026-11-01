"use client";

interface Violation { metric: string; budget: number; actual: number; }
interface Report { path: string; withinBudget: boolean; score: number; violations: Violation[]; }
interface Props { reports: Report[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudgetCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Performance Budget</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {reports.length} endpoints</p>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No performance budgets</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.path} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{r.path}</code>
                <span className={`font-bold ${r.score >= 75 ? "text-green-600" : r.score >= 50 ? "text-amber-600" : "text-red-600"}`}>{r.score}%</span>
              </div>
              {r.violations.length > 0 && (
                <div className="mt-1 text-[10px] text-red-400">
                  {r.violations.map((v) => `${v.metric}: ${v.actual}ms (budget: ${v.budget}ms)`).join(" · ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

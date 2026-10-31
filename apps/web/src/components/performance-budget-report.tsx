"use client";

interface BudgetResult { metric: string; budget: number; actual: number; over_budget: boolean; usage_pct: number; }
interface PerformanceBudgetReportProps { results: BudgetResult[]; violations: number; allWithin: boolean; }

const metricLabels: Record<string, string> = {
  js_size_kb: "JS Size", css_size_kb: "CSS Size", image_size_kb: "Images",
  total_size_kb: "Total Size", first_paint_ms: "First Paint", fcp_ms: "FCP",
  lcp_ms: "LCP", tti_ms: "TTI", cls: "CLS",
};

export function PerformanceBudgetReport({ results, violations, allWithin }: PerformanceBudgetReportProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Performance Budget</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${allWithin ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {allWithin ? "✅ Within Budget" : `⚠️ ${violations} over`}
        </span>
      </div>
      <div className="space-y-1.5">
        {results.map(r => (
          <div key={r.metric} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
            <span className={r.over_budget ? "text-red-500" : "text-green-500"}>{r.over_budget ? "✗" : "✓"}</span>
            <span className="w-24 text-sm">{metricLabels[r.metric] ?? r.metric}</span>
            <div className="flex-1">
              <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${r.over_budget ? "bg-red-500" : "bg-green-500"}`}
                  style={{ width: `${Math.min(r.usage_pct, 100)}%` }} />
              </div>
            </div>
            <span className="w-24 text-right text-xs text-gray-400">{r.actual} / {r.budget}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

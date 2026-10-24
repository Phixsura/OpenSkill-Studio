"use client";

interface Check { metric: string; passed: boolean; baseline?: number; canary?: number; diff?: number; diff_pct?: number; }
interface CanaryAnalysisReportProps { verdict: string; checks: Check[]; confidence: number;
  onPromote: () => void; onRollback: () => void; }

export function CanaryAnalysisReport({ verdict, checks, confidence, onPromote, onRollback }: CanaryAnalysisReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Canary Analysis</h2>
        <span className={`rounded-full px-3 py-1 text-sm font-bold ${verdict === "promote" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {verdict === "promote" ? "✅ Safe to Promote" : "❌ Rollback Recommended"}
        </span>
      </div>
      <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
        <p className="text-2xl font-bold">{confidence}%</p>
        <p className="text-xs text-gray-400">Confidence</p>
      </div>
      <div className="space-y-1.5">
        {checks.map(c => (
          <div key={c.metric} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{c.passed ? "✅" : "❌"}</span>
              <span className="text-sm font-medium">{c.metric.replace(/_/g, " ")}</span>
            </div>
            <span className="text-xs text-gray-400">
              {c.baseline !== undefined ? `${c.baseline} → ${c.canary}` : `${c.canary}`}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <button onClick={onPromote} disabled={verdict !== "promote"}
          className="flex-1 rounded bg-green-600 py-2 text-sm text-white disabled:opacity-50">Promote</button>
        <button onClick={onRollback}
          className="flex-1 rounded border border-red-300 py-2 text-sm text-red-600">Rollback</button>
      </div>
    </div>
  );
}

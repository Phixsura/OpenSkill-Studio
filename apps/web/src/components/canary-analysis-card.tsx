"use client";

interface MetricComparison { baseline: number; canary: number; deltaPct: number;
  regression: boolean; improvement: boolean; }
interface CanaryAnalysisCardProps { metrics: Record<string, MetricComparison>;
  verdict: string; action: string; reason: string; }

export function CanaryAnalysisCard({ metrics, verdict, action, reason }: CanaryAnalysisCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${verdict === "pass" ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">🐤 Canary Analysis</h3>
        <span className={`text-xs font-medium ${verdict === "pass" ? "text-green-600" : "text-red-500"}`}>
          {verdict === "pass" ? "✅ Pass — Promote" : "❌ Fail — Rollback"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(metrics).map(([name, m]) => (
          <div key={name} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className={m.regression ? "text-red-600 font-bold" : m.improvement ? "text-green-600" : ""}>{name}</span>
            <span className="font-mono">{m.baseline} → {m.canary} ({m.deltaPct > 0 ? "+" : ""}{m.deltaPct}%)</span>
          </div>
        ))}
      </div>
      <div className="p-3 text-xs text-gray-500 border-t dark:border-gray-700">{reason}</div>
    </div>
  );
}

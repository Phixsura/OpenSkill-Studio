"use client";
interface PerfBaselinePanelProps { endpoint: string; baselineP99: number; currentP99: number;
  p99ChangePct: number; verdict: string; }
const VERDICT_STYLE: Record<string, string> = { stable: "text-green-600", regression: "text-red-500", improved: "text-blue-500" };
export function PerfBaselinePanel({ endpoint, baselineP99, currentP99, p99ChangePct, verdict }: PerfBaselinePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📏 Perf Baseline</h3>
        <span className={`text-xs font-bold ${VERDICT_STYLE[verdict] ?? ""}`}>
          {endpoint} · {verdict} ({p99ChangePct > 0 ? "+" : ""}{p99ChangePct}%)
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Baseline P99</span><div className="font-bold text-lg">{baselineP99}ms</div></div>
        <div><span className="text-gray-400">Current P99</span>
          <div className={`font-bold text-lg ${verdict === "regression" ? "text-red-500" : ""}`}>{currentP99}ms</div></div>
      </div>
    </div>
  );
}

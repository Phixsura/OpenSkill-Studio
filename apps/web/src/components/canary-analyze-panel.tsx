"use client";
interface CanaryAnalyzePanelProps { verdict: string; confidencePct: number; errorDelta: number;
  latencyDeltaPct: number; successRate: number; checks: Record<string, boolean>; }
const VERDICT_STYLE: Record<string, string> = { promote: "text-green-600", rollback: "text-red-600", hold: "text-yellow-600" };
export function CanaryAnalyzePanel({ verdict, confidencePct, errorDelta, latencyDeltaPct, successRate, checks }: CanaryAnalyzePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐤 Canary Analysis</h3>
        <span className={`text-sm font-bold uppercase ${VERDICT_STYLE[verdict] ?? ""}`}>{verdict} ({confidencePct}%)</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Error Δ</span><div className={`font-bold ${checks.err_ok ? "text-green-600" : "text-red-500"}`}>{errorDelta > 0 ? "+" : ""}{errorDelta}%</div></div>
        <div><span className="text-gray-400">Latency Δ</span><div className={`font-bold ${checks.lat_ok ? "text-green-600" : "text-red-500"}`}>{latencyDeltaPct > 0 ? "+" : ""}{latencyDeltaPct}%</div></div>
        <div><span className="text-gray-400">Success</span><div className={`font-bold ${checks.success_ok ? "text-green-600" : "text-red-500"}`}>{successRate}%</div></div>
      </div>
    </div>
  );
}

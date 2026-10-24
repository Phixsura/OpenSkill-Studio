"use client";
interface RolloutMonitorPanelProps { currentPct: number; health: string; recommendation: string;
  errorRate: number; p99Ms: number; errorOk: boolean; latencyOk: boolean; }
const HEALTH_STYLE: Record<string, string> = { good: "bg-green-500", bad: "bg-red-500" };
const REC_STYLE: Record<string, string> = { continue: "text-green-600", pause: "text-yellow-600", rollback: "text-red-500" };
export function RolloutMonitorPanel({ currentPct, health, recommendation, errorRate, p99Ms, errorOk, latencyOk }: RolloutMonitorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${HEALTH_STYLE[health] ?? "bg-gray-500"}`}>
        Rollout {currentPct}% — {health.toUpperCase()}
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Error Rate</span>
          <div className={`font-bold text-lg ${errorOk ? "text-green-600" : "text-red-500"}`}>{errorRate}%</div></div>
        <div><span className="text-gray-400">P99 Latency</span>
          <div className={`font-bold text-lg ${latencyOk ? "text-green-600" : "text-red-500"}`}>{p99Ms}ms</div></div>
      </div>
      <div className="border-t dark:border-gray-700 p-3 text-center">
        <span className={`text-xs font-bold ${REC_STYLE[recommendation] ?? ""}`}>Recommendation: {recommendation.toUpperCase()}</span>
      </div>
    </div>
  );
}

"use client";
interface MeshSummaryPanelProps { overall: string; totalServices: number; healthy: number;
  totalRps: number; errorRatePct: number; mtlsPct: number; avgLatencyMs: number; }
const OV_STYLE: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function MeshSummaryPanel({ overall, totalServices, healthy, totalRps, errorRatePct, mtlsPct, avgLatencyMs }: MeshSummaryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${OV_STYLE[overall] ?? "bg-gray-500"}`}>
        Service Mesh: {overall.toUpperCase()} — {healthy}/{totalServices} healthy
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">RPS</span><div className="font-bold text-lg">{totalRps.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Errors</span><div className="font-bold text-lg">{errorRatePct}%</div></div>
        <div><span className="text-gray-400">mTLS</span><div className="font-bold text-lg">{mtlsPct}%</div></div>
        <div><span className="text-gray-400">Latency</span><div className="font-bold text-lg">{avgLatencyMs}ms</div></div>
      </div>
    </div>
  );
}

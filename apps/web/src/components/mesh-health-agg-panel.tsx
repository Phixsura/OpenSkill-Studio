"use client";
interface MeshHealthAggPanelProps { overall: string; total: number; healthy: number;
  degraded: number; down: number; avgLatencyMs: number; mtlsCoveragePct: number; healthPct: number; }
const OV_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function MeshHealthAggPanel({ overall, total, healthy, degraded, down,
  avgLatencyMs, mtlsCoveragePct, healthPct }: MeshHealthAggPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${OV_COLOR[overall] ?? "bg-gray-500"}`}>
        Mesh: {overall.toUpperCase()} · {healthPct}% healthy
      </div>
      <div className="grid grid-cols-5 gap-1 p-4 text-center text-[11px]">
        <div><span className="text-gray-400">Total</span><div className="font-bold">{total}</div></div>
        <div><span className="text-gray-400">Healthy</span><div className="font-bold text-green-600">{healthy}</div></div>
        <div><span className="text-gray-400">Degraded</span><div className="font-bold text-yellow-600">{degraded}</div></div>
        <div><span className="text-gray-400">Down</span><div className={`font-bold ${down > 0 ? "text-red-500" : "text-gray-400"}`}>{down}</div></div>
        <div><span className="text-gray-400">mTLS</span><div className="font-bold">{mtlsCoveragePct}%</div></div>
      </div>
    </div>
  );
}

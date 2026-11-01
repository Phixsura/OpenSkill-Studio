"use client";
interface MeshDashFinalPanelProps { score: number; status: string; healthy: number; total: number;
  rps: number; errorRatePct: number; p99Ms: number; mtlsPct: number; circuitTrips: number; retries: number; }
const STATUS_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function MeshDashFinalPanel({ score, status, healthy, total, rps, errorRatePct,
  p99Ms, mtlsPct, circuitTrips, retries }: MeshDashFinalPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{score}/100</div>
        <div className="text-xs">Mesh: {status.toUpperCase()} · {healthy}/{total} healthy · {rps.toLocaleString()} rps</div>
      </div>
      <div className="grid grid-cols-5 gap-1 p-3 text-center text-[10px]">
        <div><span className="text-gray-400">Errors</span><div className="font-bold">{errorRatePct}%</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold">{p99Ms}ms</div></div>
        <div><span className="text-gray-400">mTLS</span><div className="font-bold">{mtlsPct}%</div></div>
        <div><span className="text-gray-400">Circuits</span><div className={`font-bold ${circuitTrips > 0 ? "text-red-500" : ""}`}>{circuitTrips}</div></div>
        <div><span className="text-gray-400">Retries</span><div className="font-bold">{retries}</div></div>
      </div>
    </div>
  );
}

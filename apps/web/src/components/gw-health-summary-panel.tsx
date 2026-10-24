"use client";
interface GwHealthSummaryPanelProps { score: number; status: string; rps: number;
  errorRatePct: number; p99Ms: number; uptimePct: number; connUtilPct: number; }
const STATUS_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function GwHealthSummaryPanel({ score, status, rps, errorRatePct, p99Ms, uptimePct, connUtilPct }: GwHealthSummaryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        <div className="text-2xl font-black">{score}/100</div>
        <div className="text-xs">Gateway {status.toUpperCase()} · {rps.toLocaleString()} rps</div>
      </div>
      <div className="grid grid-cols-4 gap-1 p-4 text-center text-[11px]">
        <div><span className="text-gray-400">Uptime</span><div className="font-bold">{uptimePct}%</div></div>
        <div><span className="text-gray-400">Errors</span><div className="font-bold">{errorRatePct}%</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold">{p99Ms}ms</div></div>
        <div><span className="text-gray-400">Conn</span><div className="font-bold">{connUtilPct}%</div></div>
      </div>
    </div>
  );
}

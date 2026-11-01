"use client";
interface GwLoadPanelProps { connUtilPct: number; rpsUtilPct: number; cpuPct: number;
  overallLoadPct: number; status: string; rps: number; connections: number; }
const STATUS_COLOR: Record<string, string> = { low: "bg-green-500", moderate: "bg-blue-500", high: "bg-yellow-500", overloaded: "bg-red-500" };
export function GwLoadPanel({ connUtilPct, rpsUtilPct, cpuPct, overallLoadPct, status, rps, connections }: GwLoadPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        Gateway Load: {status.toUpperCase()} ({overallLoadPct}%)
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Connections</span><div className="font-bold">{connUtilPct}%</div><div className="text-[10px] text-gray-400">{connections.toLocaleString()}</div></div>
        <div><span className="text-gray-400">RPS</span><div className="font-bold">{rpsUtilPct}%</div><div className="text-[10px] text-gray-400">{rps.toLocaleString()}</div></div>
        <div><span className="text-gray-400">CPU</span><div className="font-bold">{cpuPct}%</div></div>
      </div>
    </div>
  );
}

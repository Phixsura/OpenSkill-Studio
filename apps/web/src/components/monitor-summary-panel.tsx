"use client";
interface MonitorSummaryPanelProps { score: number; status: string; uptimePct: number;
  errorRatePct: number; p99Ms: number; rps: number; cpuPct: number; memoryPct: number;
  activeAlerts: number; openIncidents: number; }
const STATUS_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function MonitorSummaryPanel({ score, status, uptimePct, errorRatePct, p99Ms, rps,
  cpuPct, memoryPct, activeAlerts, openIncidents }: MonitorSummaryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        <div className="text-3xl font-black">{score}/100</div>
        <div className="text-sm">{status.toUpperCase()} · {rps.toLocaleString()} rps</div>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-[11px]">
        <div><span className="text-gray-400">Uptime</span><div className="font-bold">{uptimePct}%</div></div>
        <div><span className="text-gray-400">Errors</span><div className="font-bold">{errorRatePct}%</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold">{p99Ms}ms</div></div>
        <div><span className="text-gray-400">CPU</span><div className="font-bold">{cpuPct}%</div></div>
        <div><span className="text-gray-400">Memory</span><div className="font-bold">{memoryPct}%</div></div>
        <div><span className="text-gray-400">Alerts</span><div className={`font-bold ${activeAlerts > 0 ? "text-red-500" : ""}`}>{activeAlerts}</div></div>
        <div><span className="text-gray-400">Incidents</span><div className={`font-bold ${openIncidents > 0 ? "text-red-500" : ""}`}>{openIncidents}</div></div>
        <div><span className="text-gray-400">Score</span><div className="font-bold">{score}</div></div>
      </div>
    </div>
  );
}

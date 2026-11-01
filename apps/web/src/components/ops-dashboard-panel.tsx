"use client";
interface OpsDashboardPanelProps { score: number; status: string; uptimePct: number;
  rps: number; errorRatePct: number; p99Ms: number; activeIncidents: number;
  deploysToday: number; servicesCount: number; }
const STATUS_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function OpsDashboardPanel({ score, status, uptimePct, rps, errorRatePct, p99Ms,
  activeIncidents, deploysToday, servicesCount }: OpsDashboardPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        <div className="text-3xl font-black">{score}/100</div>
        <div className="text-sm">Platform {status.toUpperCase()} · {servicesCount} services · {rps.toLocaleString()} rps</div>
      </div>
      <div className="grid grid-cols-5 gap-1 p-4 text-center text-[11px]">
        <div><span className="text-gray-400">Uptime</span><div className="font-bold">{uptimePct}%</div></div>
        <div><span className="text-gray-400">Errors</span><div className="font-bold">{errorRatePct}%</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold">{p99Ms}ms</div></div>
        <div><span className="text-gray-400">Incidents</span><div className={`font-bold ${activeIncidents > 0 ? "text-red-500" : ""}`}>{activeIncidents}</div></div>
        <div><span className="text-gray-400">Deploys</span><div className="font-bold">{deploysToday}</div></div>
      </div>
    </div>
  );
}

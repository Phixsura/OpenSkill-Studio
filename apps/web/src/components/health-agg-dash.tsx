"use client";

interface HealthCheck { name: string; status: string; latencyMs: number; }
interface HealthAggDashProps { overall: string; checks: HealthCheck[]; uptimePct: number; avgLatencyMs: number; trend: string; }

const STATUS_DOT: Record<string, string> = { up: "bg-green-500", down: "bg-red-500", degraded: "bg-yellow-500" };
const OVERALL_STYLE: Record<string, string> = { healthy: "text-green-600", degraded: "text-yellow-600", outage: "text-red-600" };

export function HealthAggDash({ overall, checks, uptimePct, avgLatencyMs, trend }: HealthAggDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💚 System Health</h3>
        <span className={`text-xs font-bold uppercase ${OVERALL_STYLE[overall] ?? ""}`}>{overall}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Uptime</div><div className="font-bold text-lg">{uptimePct}%</div></div>
        <div><div className="text-gray-400">Avg Latency</div><div className="font-bold text-lg">{avgLatencyMs}ms</div></div>
        <div><div className="text-gray-400">Trend</div><div className="font-bold text-lg">{trend}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${STATUS_DOT[c.status] ?? "bg-gray-400"}`} />
              <span>{c.name}</span>
            </div>
            <span className="text-gray-400">{c.latencyMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}

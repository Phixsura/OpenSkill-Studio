"use client";
interface GwInfo { name: string; region: string; status: string; latencyMs: number; }
interface GwHealthPanelProps { gateways: GwInfo[]; allHealthy: boolean; avgLatencyMs: number; }
const DOT: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500" };
export function GwHealthPanel({ gateways, allHealthy, avgLatencyMs }: GwHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚪 Gateway Health</h3>
        <span className={`text-xs font-bold ${allHealthy ? "text-green-600" : "text-yellow-600"}`}>
          {allHealthy ? "✅ All healthy" : "⚠ Issues"} · avg {avgLatencyMs}ms
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {gateways.map(g => (
          <div key={g.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${DOT[g.status] ?? "bg-gray-400"}`} />
              <span className="font-mono">{g.name}</span>
              <span className="text-gray-400">{g.region}</span>
            </div>
            <span className="text-gray-400">{g.latencyMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}

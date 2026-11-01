"use client";
interface Upstream { name: string; address: string; successRate: number; avgMs: number; healthy: boolean; }
interface GwUpstreamPanelProps { upstreams: Upstream[]; healthy: number; unhealthy: number; }
export function GwUpstreamPanel({ upstreams, healthy, unhealthy }: GwUpstreamPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⬆️ Gateway Upstreams</h3>
        <span className={`text-xs ${unhealthy > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {healthy} healthy{unhealthy > 0 ? ` · ${unhealthy} unhealthy` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {upstreams.map(u => (
          <div key={u.name} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${u.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{u.name}</span>
              <span className="text-gray-400">{u.address}</span>
            </div>
            <span className="text-gray-400">{u.successRate}% · {u.avgMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}

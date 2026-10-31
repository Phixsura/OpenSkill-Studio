"use client";
interface EpHealth { endpoint: string; status: string; errorRate: number; avgMs: number; totalRequests: number; }
interface EpHealthPanelProps { endpoints: EpHealth[]; }
const STATUS_DOT: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", unhealthy: "bg-red-500" };
export function EpHealthPanel({ endpoints }: EpHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Endpoint Health</h3>
        <span className="text-xs text-gray-400">{endpoints.length} endpoints</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(ep => (
          <div key={ep.endpoint} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${STATUS_DOT[ep.status] ?? "bg-gray-400"}`} />
              <span className="font-mono">{ep.endpoint}</span>
            </div>
            <span className="text-gray-400">{ep.errorRate}% err · {ep.avgMs}ms · {ep.totalRequests} reqs</span>
          </div>
        ))}
      </div>
    </div>
  );
}

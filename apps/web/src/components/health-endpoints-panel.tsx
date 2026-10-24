"use client";
interface HealthEp { service: string; url: string; healthy: boolean; lastLatencyMs: number; consecutiveFailures: number; }
interface HealthEndpointsPanelProps { endpoints: HealthEp[]; healthy: number; total: number; }
export function HealthEndpointsPanel({ endpoints, healthy, total }: HealthEndpointsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Health Endpoints</h3>
        <span className={`text-xs font-bold ${healthy === total ? "text-green-600" : "text-yellow-600"}`}>
          {healthy}/{total} healthy
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(ep => (
          <div key={ep.service} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${ep.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{ep.service}</span>
            </div>
            <span className="text-gray-400">{ep.lastLatencyMs}ms{ep.consecutiveFailures > 0 ? ` · ${ep.consecutiveFailures} fails` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

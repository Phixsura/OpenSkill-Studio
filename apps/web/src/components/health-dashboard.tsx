"use client";

interface EndpointHealth { name: string; url: string; healthy: boolean; status_code: number; response_ms: number; }
interface HealthDashboardProps { endpoints: EndpointHealth[]; overall: string; healthy: number; unhealthy: number; }

export function HealthDashboard({ endpoints, overall, healthy, unhealthy }: HealthDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className={`h-3 w-3 rounded-full ${overall === "healthy" ? "bg-green-500" : "bg-yellow-500"}`} />
        <h3 className="text-sm font-semibold capitalize">{overall}</h3>
        <span className="text-xs text-gray-400">{healthy}↑ {unhealthy}↓</span>
      </div>
      <div className="space-y-2">
        {endpoints.map(ep => (
          <div key={ep.name} className="flex items-center justify-between rounded-lg border px-4 py-2.5 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${ep.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium">{ep.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span className="font-mono">{ep.status_code}</span>
              <span>{ep.response_ms}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

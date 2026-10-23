"use client";

interface Check { name: string; status: string; }
interface ServiceHealth { service: string; healthy: boolean; checks_passed: number;
  checks_failed: number; latency_ms: number; details: Check[]; }
interface HealthProbeDashboardProps { services: ServiceHealth[]; overallStatus: string;
  checkedAt: string; onRefresh: () => void; }

export function HealthProbeDashboard({ services, overallStatus, checkedAt, onRefresh }: HealthProbeDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`h-3 w-3 rounded-full ${overallStatus === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
          <h2 className="text-lg font-semibold">Health Probes</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{new Date(checkedAt).toLocaleTimeString()}</span>
          <button onClick={onRefresh} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Refresh</button>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {services.map(svc => (
          <div key={svc.service} className={`rounded-lg border p-3 ${svc.healthy ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{svc.service}</span>
              <span className="text-xs text-gray-400">{svc.latency_ms}ms</span>
            </div>
            <div className="mt-2 space-y-0.5">
              {svc.details.map(c => (
                <div key={c.name} className="flex items-center gap-1.5 text-xs">
                  <span>{c.status === "pass" ? "✅" : "❌"}</span>
                  <span>{c.name}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

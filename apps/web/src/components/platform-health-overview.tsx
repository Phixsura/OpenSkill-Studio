"use client";

interface ServiceHealth {
  name: string;
  status: "healthy" | "degraded" | "down";
  latencyMs: number;
  uptime: number;
}

interface PlatformMetrics {
  totalExtensions: number;
  activeOrgs: number;
  apiCallsToday: number;
  errorRate: number;
  avgLatencyMs: number;
}

export function PlatformHealthOverview({
  services,
  metrics,
  lastUpdated,
}: {
  services: ServiceHealth[];
  metrics: PlatformMetrics;
  lastUpdated: string;
}) {
  const healthy = services.filter((s) => s.status === "healthy").length;
  const degraded = services.filter((s) => s.status === "degraded").length;
  const down = services.filter((s) => s.status === "down").length;
  const allHealthy = degraded === 0 && down === 0;

  const statusDot: Record<string, string> = {
    healthy: "bg-green-500",
    degraded: "bg-yellow-500",
    down: "bg-red-500",
  };

  return (
    <div className="space-y-5">
      {/* Overall banner */}
      <div className={`rounded-xl p-5 text-center ${
        allHealthy ? "bg-green-50 dark:bg-green-900/10" : down > 0 ? "bg-red-50 dark:bg-red-900/10" : "bg-yellow-50 dark:bg-yellow-900/10"
      }`}>
        <div className="text-3xl mb-1">{allHealthy ? "✅" : down > 0 ? "🔴" : "⚠️"}</div>
        <h1 className="text-xl font-bold">
          {allHealthy ? "All Systems Operational" : down > 0 ? `${down} Service(s) Down` : `${degraded} Service(s) Degraded`}
        </h1>
        <p className="text-xs text-gray-500 mt-1">Last updated: {lastUpdated}</p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <MetricCard label="Extensions" value={metrics.totalExtensions.toLocaleString()} />
        <MetricCard label="Active Orgs" value={metrics.activeOrgs.toLocaleString()} />
        <MetricCard label="API Calls Today" value={metrics.apiCallsToday.toLocaleString()} />
        <MetricCard label="Error Rate" value={`${metrics.errorRate}%`} alert={metrics.errorRate > 1} />
        <MetricCard label="Avg Latency" value={`${metrics.avgLatencyMs}ms`} alert={metrics.avgLatencyMs > 500} />
      </div>

      {/* Services */}
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-sm">Services</h2>
          <span className="text-xs text-gray-400">{healthy}/{services.length} healthy</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {services.map((svc) => (
            <div key={svc.name} className="flex items-center justify-between rounded-lg bg-gray-50 dark:bg-gray-800 px-3 py-2">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${statusDot[svc.status]}`} />
                <span className="text-sm">{svc.name}</span>
              </div>
              <span className="text-xs text-gray-400">{svc.latencyMs}ms</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, alert }: { label: string; value: string; alert?: boolean }) {
  return (
    <div className="rounded-lg border dark:border-gray-700 p-3 text-center">
      <div className={`text-lg font-bold ${alert ? "text-red-500" : ""}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

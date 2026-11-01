"use client";

interface ApiHealthOverviewProps { totalEndpoints: number; healthy: number;
  healthPct: number; avgLatencyMs: number; avgErrorRate: number; overall: string;
  slowest: { endpoint: string; latencyMs: number } | null;
  mostErrors: { endpoint: string; errorRate: number } | null; }

export function ApiHealthOverview({ totalEndpoints, healthy, healthPct, avgLatencyMs,
  avgErrorRate, overall, slowest, mostErrors }: ApiHealthOverviewProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🩺 API Health</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          overall === "healthy" ? "bg-green-100 text-green-700" :
          overall === "degraded" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{overall} · {healthPct}%</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{totalEndpoints}</p><p className="text-xs text-gray-400">Endpoints</p></div>
        <div><p className="text-lg font-bold text-green-600">{healthy}</p><p className="text-xs text-gray-400">Healthy</p></div>
        <div><p className="text-lg font-bold">{avgLatencyMs}ms</p><p className="text-xs text-gray-400">Avg Latency</p></div>
        <div><p className="text-lg font-bold">{avgErrorRate}%</p><p className="text-xs text-gray-400">Error Rate</p></div>
      </div>
      <div className="flex gap-4 text-xs text-gray-400">
        {slowest && <span>Slowest: <code>{slowest.endpoint}</code> ({slowest.latencyMs}ms)</span>}
        {mostErrors && <span>Most errors: <code>{mostErrors.endpoint}</code> ({mostErrors.errorRate}%)</span>}
      </div>
    </div>
  );
}

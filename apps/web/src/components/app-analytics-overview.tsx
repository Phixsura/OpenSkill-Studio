"use client";

interface AppAnalyticsOverviewProps { appId: string; netDisplay: string; apiDisplay: string;
  activeUsers: number; retentionPct: number; errorRate: number;
  avgResponseMs: number; rating: number; reviews: number; health: string; }

const HEALTH_BADGE: Record<string, string> = {
  excellent: "bg-green-100 text-green-700", good: "bg-blue-100 text-blue-700",
  needs_attention: "bg-yellow-100 text-yellow-700", critical: "bg-red-100 text-red-700",
};

export function AppAnalyticsOverview({ appId, netDisplay, apiDisplay, activeUsers,
  retentionPct, errorRate, avgResponseMs, rating, reviews, health }: AppAnalyticsOverviewProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 App Analytics</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${HEALTH_BADGE[health] || ""}`}>{health.replace("_", " ")}</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-3">
        <div><p className="text-lg font-bold">{netDisplay}</p><p className="text-xs text-gray-400">Net Installs</p></div>
        <div><p className="text-lg font-bold">{apiDisplay}</p><p className="text-xs text-gray-400">API Calls</p></div>
        <div><p className="text-lg font-bold">{activeUsers.toLocaleString()}</p><p className="text-xs text-gray-400">Active Users</p></div>
        <div><p className="text-lg font-bold">⭐ {rating}</p><p className="text-xs text-gray-400">{reviews} reviews</p></div>
      </div>
      <div className="flex gap-4 text-xs text-gray-400">
        <span>Retention: {retentionPct}%</span>
        <span>Error rate: {errorRate}%</span>
        <span>Avg: {avgResponseMs}ms</span>
      </div>
    </div>
  );
}

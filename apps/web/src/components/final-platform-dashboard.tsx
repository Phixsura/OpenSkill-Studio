"use client";

interface MetricValue { value: number; display: string; }
interface FinalPlatformDashboardProps { healthDisplay: string; status: string;
  metrics: Record<string, MetricValue>; incidents: number; pendingReviews: number; }

const METRIC_ICONS: Record<string, string> = {
  apps: "📱", developers: "👩‍💻", installs: "📥", api_calls: "📡",
  uptime: "🟢", rating: "⭐", active_users: "👥", mrr: "💰",
};

export function FinalPlatformDashboard({ healthDisplay, status, metrics, incidents, pendingReviews }: FinalPlatformDashboardProps) {
  return (
    <div className="space-y-5">
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white text-center">
        <p className="text-4xl font-black">{healthDisplay}</p>
        <p className="text-sm opacity-90 capitalize">Platform Health: {status}</p>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {Object.entries(metrics).map(([key, m]) => (
          <div key={key} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <p className="text-lg">{METRIC_ICONS[key] || "📊"}</p>
            <p className="text-lg font-bold">{m.display}</p>
            <p className="text-xs text-gray-400 capitalize">{key.replace("_", " ")}</p>
          </div>
        ))}
      </div>
      {(incidents > 0 || pendingReviews > 5) && (
        <div className="flex gap-3 text-xs">
          {incidents > 0 && <span className="px-2 py-1 rounded bg-red-100 text-red-700">🚨 {incidents} incidents</span>}
          {pendingReviews > 5 && <span className="px-2 py-1 rounded bg-yellow-100 text-yellow-700">📋 {pendingReviews} pending reviews</span>}
        </div>
      )}
    </div>
  );
}

"use client";

interface RealtimeMetrics { active_users: number; requests_per_sec: number; avg_response_ms: number;
  error_rate_pct: number; cpu_pct: number; memory_pct: number; }
interface LiveMetricsDashboardProps { metrics: RealtimeMetrics; alertsActive: number; lastUpdated: string; }

export function LiveMetricsDashboard({ metrics, alertsActive, lastUpdated }: LiveMetricsDashboardProps) {
  const m = metrics;
  const cards = [
    { label: "Active Users", value: m.active_users.toLocaleString(), icon: "👥" },
    { label: "RPS", value: m.requests_per_sec.toFixed(1), icon: "⚡" },
    { label: "Latency", value: `${m.avg_response_ms}ms`, icon: "⏱️" },
    { label: "Errors", value: `${m.error_rate_pct}%`, icon: m.error_rate_pct > 1 ? "🔴" : "🟢" },
    { label: "CPU", value: `${m.cpu_pct}%`, icon: "🖥️" },
    { label: "Memory", value: `${m.memory_pct}%`, icon: "💾" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
          <h2 className="text-lg font-semibold">Live Metrics</h2>
        </div>
        <span className="text-xs text-gray-400">{new Date(lastUpdated).toLocaleTimeString()}</span>
      </div>
      {alertsActive > 0 && (
        <div className="rounded bg-red-50 p-2 text-center text-sm text-red-600 dark:bg-red-900/10">
          🚨 {alertsActive} active alert{alertsActive > 1 ? "s" : ""}
        </div>
      )}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {cards.map(c => (
          <div key={c.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <span className="text-lg">{c.icon}</span>
            <p className="text-xl font-bold">{c.value}</p>
            <p className="text-xs text-gray-400">{c.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";

interface AnalyticsDashboardProps { activeApps: number; displayRequests: string;
  avgLatencyMs: number; errorRatePct: number; dailyActiveUsers: number;
  displayRevenue: string; health: string; }

const HEALTH_COLORS: Record<string, string> = {
  excellent: "text-green-600", good: "text-blue-600", needs_improvement: "text-yellow-600",
};

export function AnalyticsDashboard({ activeApps, displayRequests, avgLatencyMs, errorRatePct, dailyActiveUsers, displayRevenue, health }: AnalyticsDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Platform Analytics</h3>
        <span className={`text-xs font-medium capitalize ${HEALTH_COLORS[health] ?? ""}`}>{health.replaceAll("_", " ")}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Apps", v: activeApps }, { l: "Requests", v: displayRequests },
          { l: "Latency", v: `${avgLatencyMs}ms` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Errors", v: `${errorRatePct}%` }, { l: "DAU", v: dailyActiveUsers.toLocaleString() },
          { l: "Revenue", v: displayRevenue }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

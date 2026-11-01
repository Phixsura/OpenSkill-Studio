"use client";

interface ServiceHealth {
  name: string;
  category: string;
  state: "healthy" | "degraded" | "critical" | "down";
  message: string;
}

interface HealthSummary {
  totalServices: number;
  overallScore: number;
  overallState: string;
  byState: Record<string, number>;
  activeIssues: number;
}

interface HealthAlert {
  serviceName: string;
  severity: "critical" | "high" | "medium";
  message: string;
  suggestedAction: string;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  healthy: { color: "text-green-600", icon: "🟢" },
  degraded: { color: "text-yellow-600", icon: "🟡" },
  critical: { color: "text-red-600", icon: "🔴" },
  down: { color: "text-gray-600", icon: "⚫" },
};

const sevColors: Record<string, string> = {
  critical: "border-red-500 bg-red-50 dark:bg-red-900/10",
  high: "border-orange-400 bg-orange-50 dark:bg-orange-900/10",
  medium: "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10",
};

export function HealthDashboardOverview({
  summary,
  services,
  alerts,
}: {
  summary: HealthSummary;
  services: ServiceHealth[];
  alerts: HealthAlert[];
}) {
  const scoreColor = summary.overallScore >= 90 ? "text-green-600" : summary.overallScore >= 60 ? "text-yellow-600" : "text-red-600";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🏥 Platform Health</h2>
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-bold ${scoreColor}`}>{summary.overallScore}</span>
          <span className="text-sm text-gray-500">/ 100</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center">
        {(["healthy", "degraded", "critical", "down"] as const).map((state) => (
          <div key={state} className="rounded-lg border dark:border-gray-700 p-2">
            <span className="text-lg">{stateConfig[state].icon}</span>
            <span className="block font-bold text-lg">{summary.byState[state] || 0}</span>
            <span className="text-xs text-gray-500 capitalize">{state}</span>
          </div>
        ))}
      </div>

      {alerts.length > 0 && (
        <div className="space-y-1">
          <span className="text-sm font-semibold">⚠ Active Issues ({alerts.length})</span>
          {alerts.map((alert, i) => (
            <div key={i} className={`rounded-lg border-l-4 p-3 ${sevColors[alert.severity]}`}>
              <div className="text-sm font-medium">{alert.message}</div>
              <div className="text-xs text-gray-500 mt-0.5">💡 {alert.suggestedAction}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-1 sm:grid-cols-3">
        {services.map((svc) => {
          const cfg = stateConfig[svc.state];
          return (
            <div key={svc.name} className="flex items-center gap-1.5 rounded-lg border dark:border-gray-700 px-2 py-1.5 text-xs">
              <span>{cfg.icon}</span>
              <span className="truncate">{svc.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

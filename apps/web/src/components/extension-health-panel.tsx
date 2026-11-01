"use client";

interface HealthMetrics {
  extensionId: string;
  status: "healthy" | "degraded" | "unhealthy" | "unknown";
  uptime: number;
  avgResponseMs: number;
  errorRate: number;
  lastCheck: string;
  incidents: { id: string; message: string; severity: string; timestamp: string }[];
}

export function ExtensionHealthPanel({ metrics }: { metrics: HealthMetrics }) {
  const statusConfig = {
    healthy: { color: "bg-green-500", text: "text-green-600 dark:text-green-400", label: "Healthy", icon: "✅" },
    degraded: { color: "bg-yellow-500", text: "text-yellow-600 dark:text-yellow-400", label: "Degraded", icon: "⚠️" },
    unhealthy: { color: "bg-red-500", text: "text-red-600 dark:text-red-400", label: "Unhealthy", icon: "❌" },
    unknown: { color: "bg-gray-400", text: "text-gray-500", label: "Unknown", icon: "❓" },
  };

  const cfg = statusConfig[metrics.status];

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-lg">🏥 Extension Health</h3>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${cfg.color} animate-pulse`} />
          <span className={`font-semibold text-sm ${cfg.text}`}>{cfg.icon} {cfg.label}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-3">
          <div className="text-xl font-bold">{metrics.uptime.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Uptime</div>
        </div>
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-3">
          <div className="text-xl font-bold">{metrics.avgResponseMs}ms</div>
          <div className="text-xs text-gray-500">Avg Response</div>
        </div>
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-3">
          <div className={`text-xl font-bold ${metrics.errorRate > 5 ? "text-red-500" : "text-green-500"}`}>
            {metrics.errorRate}%
          </div>
          <div className="text-xs text-gray-500">Error Rate</div>
        </div>
      </div>

      <div className="text-xs text-gray-400">Last checked: {metrics.lastCheck}</div>

      {metrics.incidents.length > 0 && (
        <div>
          <h4 className="font-medium text-sm mb-2">Recent Incidents</h4>
          <div className="space-y-1">
            {metrics.incidents.map((inc) => (
              <div key={inc.id} className="flex items-center justify-between text-sm py-1 border-b dark:border-gray-800 last:border-0">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    inc.severity === "critical" ? "bg-red-500" : inc.severity === "warning" ? "bg-yellow-500" : "bg-blue-500"
                  }`} />
                  <span>{inc.message}</span>
                </div>
                <span className="text-xs text-gray-400">{inc.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

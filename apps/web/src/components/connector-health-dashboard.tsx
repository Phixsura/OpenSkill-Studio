"use client";

interface ConnectorHealth {
  id: string;
  name: string;
  icon: string;
  status: "operational" | "degraded" | "outage" | "maintenance";
  uptimePercent: number;
  avgLatencyMs: number;
  lastIncident: string;
  eventsLast24h: number;
  errorRate: number;
}

export function ConnectorHealthDashboard({
  connectors,
  overallStatus,
}: {
  connectors: ConnectorHealth[];
  overallStatus: string;
}) {
  const statusConfig: Record<string, { color: string; dot: string; label: string }> = {
    operational: { color: "text-green-500", dot: "bg-green-500", label: "Operational" },
    degraded: { color: "text-yellow-500", dot: "bg-yellow-500", label: "Degraded" },
    outage: { color: "text-red-500", dot: "bg-red-500", label: "Outage" },
    maintenance: { color: "text-blue-500", dot: "bg-blue-500", label: "Maintenance" },
  };

  const operational = connectors.filter((c) => c.status === "operational").length;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔌 Connector Health</h2>
        <div className="flex items-center gap-2 text-sm">
          <div className={`w-2.5 h-2.5 rounded-full ${statusConfig[overallStatus]?.dot || "bg-gray-400"}`} />
          <span className={statusConfig[overallStatus]?.color}>{overallStatus}</span>
          <span className="text-gray-400">· {operational}/{connectors.length} operational</span>
        </div>
      </div>

      <div className="space-y-2">
        {connectors.map((conn) => {
          const cfg = statusConfig[conn.status];
          return (
            <div key={conn.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{conn.icon}</span>
                  <div>
                    <span className="font-semibold text-sm">{conn.name}</span>
                    <div className="flex items-center gap-1 mt-0.5">
                      <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                      <span className={`text-xs ${cfg.color}`}>{cfg.label}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right text-xs text-gray-400">
                  <div>Uptime: <span className={conn.uptimePercent >= 99.9 ? "text-green-500 font-bold" : conn.uptimePercent >= 99 ? "" : "text-red-500"}>{conn.uptimePercent}%</span></div>
                  <div>Latency: {conn.avgLatencyMs}ms</div>
                </div>
              </div>
              <div className="flex gap-4 text-xs text-gray-400">
                <span>Events 24h: {conn.eventsLast24h.toLocaleString()}</span>
                <span>Error rate: <span className={conn.errorRate > 1 ? "text-red-400" : "text-green-400"}>{conn.errorRate}%</span></span>
                {conn.lastIncident && <span>Last incident: {conn.lastIncident}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";

interface ConnectorHealth {
  connectorId: string;
  name: string;
  endpointUrl: string;
  status: "healthy" | "degraded" | "down" | "unknown";
  uptimePercent: number;
  avgResponseMs: number;
  lastChecked?: string;
  meetsSla: boolean;
}

const statusConfig: Record<string, { color: string; icon: string; bg: string }> = {
  healthy: { color: "text-green-600", icon: "🟢", bg: "bg-green-100 dark:bg-green-900/30" },
  degraded: { color: "text-yellow-600", icon: "🟡", bg: "bg-yellow-100 dark:bg-yellow-900/30" },
  down: { color: "text-red-600", icon: "🔴", bg: "bg-red-100 dark:bg-red-900/30" },
  unknown: { color: "text-gray-500", icon: "⚪", bg: "bg-gray-100 dark:bg-gray-800" },
};

export function ConnectorHealthPanel({
  connectors,
  onRefresh,
}: {
  connectors: ConnectorHealth[];
  onRefresh?: (id: string) => void;
}) {
  const healthy = connectors.filter((c) => c.status === "healthy").length;
  const total = connectors.length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔌 Connector Health</h2>
        <span className="text-sm">
          <span className="text-green-600 font-bold">{healthy}</span>
          <span className="text-gray-400">/{total} healthy</span>
        </span>
      </div>

      <div className="space-y-2">
        {connectors.map((c) => {
          const cfg = statusConfig[c.status];
          return (
            <div key={c.connectorId} className={`rounded-xl border dark:border-gray-700 p-4 ${c.status === "down" ? "border-red-300 dark:border-red-700" : ""}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{c.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.bg} ${cfg.color}`}>{c.status}</span>
                </div>
                <button onClick={() => onRefresh?.(c.connectorId)}
                  className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Check</button>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-gray-400 block">Uptime</span>
                  <span className={`font-bold ${c.uptimePercent >= 99.9 ? "text-green-600" : c.uptimePercent >= 95 ? "text-yellow-600" : "text-red-600"}`}>
                    {c.uptimePercent}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 block">Avg Response</span>
                  <span className="font-bold">{c.avgResponseMs}ms</span>
                </div>
                <div>
                  <span className="text-gray-400 block">SLA</span>
                  <span className={`font-bold ${c.meetsSla ? "text-green-600" : "text-red-600"}`}>
                    {c.meetsSla ? "✓ Met" : "✗ Breach"}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

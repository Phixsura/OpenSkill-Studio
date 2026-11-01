"use client";

interface ConnectorStatus {
  id: string;
  name: string;
  icon: string;
  status: "connected" | "disconnected" | "error" | "syncing";
  lastSync: string;
  eventsProcessed: number;
  errorCount: number;
  latencyMs: number;
}

export function ConnectorStatusPanel({
  connectors,
  onReconnect,
  onDisconnect,
}: {
  connectors: ConnectorStatus[];
  onReconnect?: (id: string) => void;
  onDisconnect?: (id: string) => void;
}) {
  const statusConfig = {
    connected: { dot: "bg-green-500", badge: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", label: "Connected" },
    disconnected: { dot: "bg-gray-400", badge: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300", label: "Disconnected" },
    error: { dot: "bg-red-500", badge: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300", label: "Error" },
    syncing: { dot: "bg-blue-500 animate-pulse", badge: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300", label: "Syncing" },
  };

  const connected = connectors.filter((c) => c.status === "connected").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔌 Connector Status</h2>
        <span className="text-sm text-gray-500">{connected}/{connectors.length} connected</span>
      </div>

      <div className="space-y-2">
        {connectors.map((conn) => {
          const cfg = statusConfig[conn.status];
          return (
            <div key={conn.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{conn.icon}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{conn.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.badge}`}>
                        <span className={`inline-block w-1.5 h-1.5 rounded-full mr-1 ${cfg.dot}`} />
                        {cfg.label}
                      </span>
                    </div>
                    <div className="flex gap-4 text-xs text-gray-400 mt-1">
                      <span>Last sync: {conn.lastSync}</span>
                      <span>Events: {conn.eventsProcessed.toLocaleString()}</span>
                      <span>Latency: {conn.latencyMs}ms</span>
                      {conn.errorCount > 0 && (
                        <span className="text-red-400">{conn.errorCount} errors</span>
                      )}
                    </div>
                  </div>
                </div>
                <div>
                  {conn.status === "connected" ? (
                    <button
                      onClick={() => onDisconnect?.(conn.id)}
                      className="text-xs text-red-500 hover:text-red-700 px-3 py-1 rounded border border-red-200 dark:border-red-800"
                    >
                      Disconnect
                    </button>
                  ) : (
                    <button
                      onClick={() => onReconnect?.(conn.id)}
                      className="text-xs text-blue-600 hover:text-blue-800 px-3 py-1 rounded border border-blue-200 dark:border-blue-800"
                    >
                      Reconnect
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

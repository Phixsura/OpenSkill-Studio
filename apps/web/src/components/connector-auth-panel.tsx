"use client";

interface ConnectorCredential {
  id: string;
  connectorId: string;
  connectorName: string;
  authType: "oauth2" | "api_key" | "basic" | "bearer";
  status: "connected" | "disconnected" | "expired" | "error";
  scopes: string[];
  expired: boolean;
}

const authIcons: Record<string, string> = {
  oauth2: "🔐", api_key: "🔑", basic: "👤", bearer: "🎫",
};

const statusStyles: Record<string, { color: string; label: string }> = {
  connected: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Connected" },
  disconnected: { color: "bg-gray-100 text-gray-500 dark:bg-gray-800", label: "Disconnected" },
  expired: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", label: "Expired" },
  error: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", label: "Error" },
};

export function ConnectorAuthPanel({
  credentials,
  onConnect,
  onDisconnect,
  onRefresh,
}: {
  credentials: ConnectorCredential[];
  onConnect?: (connectorId: string) => void;
  onDisconnect?: (id: string) => void;
  onRefresh?: (id: string) => void;
}) {
  const connected = credentials.filter((c) => c.status === "connected").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔗 Connector Auth</h2>
        <span className="text-sm text-gray-500">{connected}/{credentials.length} connected</span>
      </div>

      <div className="space-y-2">
        {credentials.map((cred) => {
          const cfg = statusStyles[cred.status];
          return (
            <div key={cred.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{authIcons[cred.authType]}</span>
                  <span className="font-semibold text-sm">{cred.connectorName}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                  <span className="text-xs text-gray-400">{cred.authType}</span>
                </div>
                <div className="flex gap-1">
                  {cred.status === "expired" && (
                    <button onClick={() => onRefresh?.(cred.id)}
                      className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Refresh</button>
                  )}
                  {cred.status === "connected" && (
                    <button onClick={() => onDisconnect?.(cred.id)}
                      className="text-xs bg-gray-600 text-white px-2 py-1 rounded">Disconnect</button>
                  )}
                  {cred.status === "disconnected" && (
                    <button onClick={() => onConnect?.(cred.connectorId)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Connect</button>
                  )}
                </div>
              </div>
              {cred.scopes.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {cred.scopes.map((s) => (
                    <span key={s} className="text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-600 px-1.5 py-0.5 rounded">{s}</span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

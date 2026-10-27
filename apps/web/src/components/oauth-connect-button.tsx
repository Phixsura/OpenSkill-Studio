"use client";

interface ConnectorAuth { connectorId: string; name: string; icon: string; connected: boolean; scopes: string[]; }

export function OAuthConnectButton({ connectors, onConnect, onDisconnect }: {
  connectors: ConnectorAuth[]; onConnect?: (id: string) => void; onDisconnect?: (id: string) => void;
}) {
  return (
    <div className="space-y-2">
      {connectors.map(c => (
        <div key={c.connectorId} className="flex items-center justify-between border dark:border-gray-700 rounded-xl p-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{c.icon}</span>
            <div>
              <span className="font-medium text-sm block">{c.name}</span>
              <span className="text-xs text-gray-500">{c.scopes.join(", ")}</span>
            </div>
          </div>
          {c.connected ? (
            <div className="flex items-center gap-2">
              <span className="text-xs text-green-600 font-medium">Connected ✓</span>
              <button onClick={() => onDisconnect?.(c.connectorId)} className="text-xs text-red-400 hover:text-red-600">Disconnect</button>
            </div>
          ) : (
            <button onClick={() => onConnect?.(c.connectorId)} className="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg">Connect</button>
          )}
        </div>
      ))}
    </div>
  );
}

"use client";

interface OAuthProvider { id: string; name: string; icon: string; color: string; }
interface OAuthConnectButtonProps { provider: OAuthProvider; connected: boolean;
  onConnect: () => void; onDisconnect: () => void; }

export function OAuthConnectButton({ provider, connected, onConnect, onDisconnect }: OAuthConnectButtonProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{provider.icon}</span>
        <div>
          <p className="text-sm font-semibold">{provider.name}</p>
          <p className="text-xs text-gray-400">{connected ? "Connected" : "Not connected"}</p>
        </div>
      </div>
      {connected ? (
        <button onClick={onDisconnect}
          className="rounded border px-3 py-1.5 text-xs text-red-600 hover:bg-red-50 dark:border-gray-600 dark:hover:bg-red-900/10">
          Disconnect
        </button>
      ) : (
        <button onClick={onConnect}
          className="rounded px-3 py-1.5 text-xs text-white" style={{ backgroundColor: provider.color }}>
          Connect
        </button>
      )}
    </div>
  );
}

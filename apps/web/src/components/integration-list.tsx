"use client";

interface Integration { id: string; label: string; icon: string; category: string; connected: boolean; }
interface IntegrationListProps { integrations: Integration[]; connected: number;
  onConnect: (id: string) => void; onDisconnect: (id: string) => void; }

export function IntegrationList({ integrations, connected, onConnect, onDisconnect }: IntegrationListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Integrations</h3>
        <span className="text-xs text-gray-400">{connected} connected</span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {integrations.map(i => (
          <div key={i.id} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-lg">{i.icon}</span>
              <div>
                <p className="text-sm font-medium">{i.label}</p>
                <p className="text-xs text-gray-400">{i.category}</p>
              </div>
            </div>
            {i.connected ? (
              <button onClick={() => onDisconnect(i.id)}
                className="rounded border px-2 py-1 text-xs text-red-600 dark:border-gray-600">Disconnect</button>
            ) : (
              <button onClick={() => onConnect(i.id)}
                className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Connect</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

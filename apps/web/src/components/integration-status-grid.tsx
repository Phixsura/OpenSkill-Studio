"use client";

interface Integration { name: string; provider: string; status: string; lastSync: string; icon: string; }
interface IntegrationStatusGridProps { integrations: Integration[]; connected: number; total: number; }

export function IntegrationStatusGrid({ integrations, connected, total }: IntegrationStatusGridProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔗 Integrations</h3>
        <span className="text-xs text-gray-400">{connected}/{total} connected</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {integrations.map(i => (
          <div key={i.name} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 ${
            i.status === "connected" ? "bg-green-50 dark:bg-green-900/10" : "bg-gray-50 dark:bg-gray-800"
          }`}>
            <span className="text-2xl">{i.icon}</span>
            <div>
              <p className="text-sm font-medium">{i.name}</p>
              <p className="text-xs text-gray-400">
                {i.status === "connected" ? `✓ ${i.lastSync}` : "Disconnected"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

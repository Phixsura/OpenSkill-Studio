"use client";

interface Integration { id: string; name: string; icon: string; category: string; description: string; popular: boolean; }
interface IntegrationCatalogGridProps { integrations: Integration[]; onConnect: (id: string) => void; }

export function IntegrationCatalogGrid({ integrations, onConnect }: IntegrationCatalogGridProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Integrations</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {integrations.map(i => (
          <div key={i.id} className="rounded-lg border p-4 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{i.icon}</span>
              <div>
                <p className="font-medium">{i.name}</p>
                {i.popular && <span className="text-[10px] text-yellow-500">⭐ Popular</span>}
              </div>
            </div>
            <p className="mt-2 text-xs text-gray-400">{i.description}</p>
            <button onClick={() => onConnect(i.id)}
              className="mt-3 w-full rounded bg-blue-600 py-1.5 text-xs text-white">Connect</button>
          </div>
        ))}
      </div>
    </div>
  );
}

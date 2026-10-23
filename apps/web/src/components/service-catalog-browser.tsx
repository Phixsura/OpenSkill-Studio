"use client";

interface CatalogService { id: string; name: string; team: string; tier: string;
  description: string; dependencies: string[]; }
interface ServiceCatalogBrowserProps { services: CatalogService[];
  byTeam: Record<string, number>; onSelect: (id: string) => void; }

const TIER_BADGE: Record<string, string> = {
  tier0: "bg-red-100 text-red-700", tier1: "bg-yellow-100 text-yellow-700",
  tier2: "bg-blue-100 text-blue-700", tier3: "bg-gray-100 text-gray-600",
};

export function ServiceCatalogBrowser({ services, byTeam, onSelect }: ServiceCatalogBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Service Catalog</h3>
        <span className="text-xs text-gray-400">{services.length} services</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <button key={s.id} onClick={() => onSelect(s.id)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
            <div className="flex items-center justify-between mb-0.5">
              <span className="text-sm font-medium">{s.name}</span>
              <div className="flex gap-1">
                <span className={`text-xs px-1.5 py-0.5 rounded ${TIER_BADGE[s.tier] || ""}`}>{s.tier}</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-500">{s.team}</span>
              </div>
            </div>
            {s.description && <p className="text-xs text-gray-400">{s.description}</p>}
            {s.dependencies.length > 0 && (
              <p className="text-xs text-gray-300 mt-0.5">Deps: {s.dependencies.join(", ")}</p>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

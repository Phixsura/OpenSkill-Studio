"use client";

interface CatalogService { name: string; owner: string; tier: string; tags: string[]; dependencies: string[]; }
interface SvcCatalogBrowserProps { services: CatalogService[]; total: number; }

const TIER_STYLE: Record<string, string> = {
  critical: "bg-red-100 text-red-700", standard: "bg-gray-100 text-gray-700",
  premium: "bg-purple-100 text-purple-700",
};

export function SvcCatalogBrowser({ services, total }: SvcCatalogBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Service Catalog</h3>
        <span className="text-xs text-gray-400">{total} services</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="px-4 py-2">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold">{s.name}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${TIER_STYLE[s.tier] ?? ""}`}>{s.tier}</span>
            </div>
            <div className="text-[10px] text-gray-400">
              {s.owner} · {s.tags.join(", ")}
              {s.dependencies.length > 0 && <span> · deps: {s.dependencies.join(", ")}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

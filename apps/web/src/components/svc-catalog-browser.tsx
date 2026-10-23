"use client";

interface CatalogService { name: string; description: string; tier: string;
  owner: string; status: string; }
interface SvcCatalogBrowserProps { services: CatalogService[]; total: number;
  healthy: number; byTier: Record<string, number>; }

const TIER_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-700", standard: "bg-blue-100 text-blue-700",
  internal: "bg-gray-100 text-gray-700",
};

export function SvcCatalogBrowser({ services, total, healthy, byTier }: SvcCatalogBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Service Catalog</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{total} services</span>
          <span className="text-green-600">{healthy} healthy</span>
        </div>
      </div>
      <div className="flex gap-2 px-4 py-2 border-b dark:border-gray-700">
        {Object.entries(byTier).map(([tier, count]) => (
          <span key={tier} className={`px-2 py-0.5 text-[10px] rounded-full ${TIER_COLORS[tier] ?? "bg-gray-100"}`}>
            {tier}: {count}
          </span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm font-medium">{s.name}</div>
              <div className="text-[10px] text-gray-400">{s.description} · {s.owner}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${s.status === "healthy" ? "bg-green-500" : "bg-yellow-500"}`} />
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${TIER_COLORS[s.tier] ?? ""}`}>{s.tier}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";

interface Feature { name: string; status: string; module: string; }
interface FeatureCatalogProps { features: Feature[]; total: number;
  gaPct: number; modules: string[]; }

const STATUS_BADGE: Record<string, string> = {
  ga: "bg-green-100 text-green-700", beta: "bg-blue-100 text-blue-700",
  alpha: "bg-purple-100 text-purple-700", deprecated: "bg-gray-200 text-gray-600",
};

export function FeatureCatalog({ features, total, gaPct, modules }: FeatureCatalogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Feature Catalog</h3>
        <span className="text-xs text-gray-400">{total} features · {gaPct}% GA</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {features.map(f => (
          <div key={f.name} className="flex items-center justify-between px-4 py-2">
            <span className="text-sm">{f.name}</span>
            <div className="flex gap-2">
              <span className="text-[10px] text-gray-400">{f.module}</span>
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${STATUS_BADGE[f.status] ?? ""}`}>{f.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
